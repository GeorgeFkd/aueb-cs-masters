import dotenv from "dotenv"
import {Octokit} from "octokit";
import commandLineArgs from "command-line-args"
import "node:https"
import "node:fs"
import * as fs from "node:fs";
import "node:assert"

import {
    CliOptions,
    GhAnalysisResults,
    IssueDetails,
    IssueInteractionsMap, NpmsSearchResponse,
    PRDetails,
    PRInteractionsMap,
    PRState
} from "./types";

import {persistResultToStorage} from "./db";
import {extractOwnerAndRepoNameFromUrl} from "./utils";
dotenv.config()



console.log("Checking if GITHUB_API_KEY variable is set");
if (!process.env.GITHUB_API_KEY) {
    console.log("Please set GITHUB_API_KEY to continue");
    process.exit(1);
}
console.log("Progress: GITHUB_API_KEY is set to: ", process.env.GITHUB_API_KEY);

const octokit = new Octokit({
    auth:process.env.GITHUB_API_KEY,
    throttle: {
        onRateLimit: (retryAfter, options, octokit, retryCount) => {
            octokit.log.warn(
                `Request quota exhausted for request ${options.method} ${options.url}`,
            );

            if (retryCount < 2) {
                // only retries twice
                octokit.log.info(`Retrying after ${retryAfter} seconds!`);
                return true;
            }
        },
        onSecondaryRateLimit: (retryAfter, options, octokit) => {
            // does not retry, only logs a warning
            octokit.log.warn(
                `SecondaryRateLimit detected for request ${options.method} ${options.url}`,
            );
        },
    },
});

async function getMostPopularFossPackagesFromNPM(options:CliOptions) {
    //not using the url type as its serialisation seemed to cause problems
    let npmsIOBaseUrl = "https://api.npms.io/v2/search?q="
    let finalQuery = options.query;
    if (options.keywords.length > 0) {
        finalQuery += "+keywords:"
        options.keywords.forEach(keyword => {
            finalQuery += keyword + ','
        })
        //remove the last comma
        finalQuery = finalQuery.substring(0, finalQuery.length - 1);
    }
    finalQuery += "+popularity-weight:" + options.popularity_weight;
    finalQuery += "+quality-weight:" + options.quality_weight;
    finalQuery += "+maintenance-weight:" + options.maintenance_weight;
    npmsIOBaseUrl += finalQuery;
    //The total number of results to return (max of 250)
    // Default value: 25
    console.log("The url being hit is: " ,npmsIOBaseUrl.toString())
    return await fetch(npmsIOBaseUrl)
}

//Get Most Popular NPM packages according to some user input
//From those, gather the github repositories
//For each github repo:
// Grab (merged) Pull requests -> Who code reviews who? + Who participates in successfull PRs
// Grab resolved(+ maybe closed) issues -> Who participates in the discussion in issues?




const cliOptions = [
    {
        name:"query", alias:"q",type:String,defaultValue:"react"
    },
    {
        name:"keywords",alias:"k",type:String,multiple:true,defaultValue:[]
    },
    {
        name:"num_top_packages",alias:"n",type:Number,defaultValue:50
    },
    {
        name:"popularity_weight",alias:"p",type:Number,defaultValue:100
    },
    {
        name:"quality_weight",alias:"u",type:Number,defaultValue: 2
    },
    {
        name:"maintenance_weight",alias:"m",type:Number,defaultValue:5
    }
]

function getUserInput() {
    const options = commandLineArgs(cliOptions) as CliOptions
    return options
}

const userQuery = getUserInput();
const result = await getMostPopularFossPackagesFromNPM(userQuery);
if (!result.ok){
    console.log(`Something went wrong: ${result.statusText}, ${await result.json()}`)
    process.exit(1)
}

const body = await result.json() as NpmsSearchResponse;
if(!body.results || body.total === 0) {
    console.log("Something went wrong with the NPM package search response")
    process.exit(1)
}
const githubRepos = body.results
    .filter(s=> s.package.links.repository !== undefined &&
    s.package.links.repository !== null &&
    s.package.links.repository.startsWith("https://github.com"));

console.log("Creating tables of sqlite db")

let failedRepos = []
for (const repo of githubRepos) {
    try {
        const repoUrl = repo.package.links.repository;
        const timerID = `github-repo-processing:${repoUrl}`
        console.log("Processing: ",repoUrl)
        console.time(timerID)
        const parsedUrl = new URL(repoUrl);
        const ghInfo = extractOwnerAndRepoNameFromUrl(parsedUrl);
        const analysisResult = await analyzeRepository(ghInfo.owner, ghInfo.repo);
        await persistResultToStorage(analysisResult);
        console.timeEnd(timerID)
    } catch (error) {
        console.error(`Failed to process repository ${repo.package.links.repository}:`, error);
        failedRepos.push(repo);
    }
}

console.log(`Failed in these repos ${failedRepos}`)

async function getMergedPullRequests(owner: string, repo: string,state:PRState,page: number | null) {
    // assert(state != null)
    const { data: pullRequests } = await octokit.rest.pulls.list({
        owner,
        repo,
        state,
        per_page: 50, // Adjust as needed, max 100 per page
        page:page || 1
    });

    return pullRequests.filter(pr => pr.merged_at);
}

async function getIssues(owner: string, repo: string,state:PRState) {
    const { data: issues } = await octokit.rest.issues.listForRepo({
        owner,
        repo,
        state,
        per_page: 50 // Adjust as needed
    });

    return issues;
}

async function getIssueDetails(owner: string, repo: string, issueNumber: number, author: string): Promise<IssueDetails> {

    const { data: comments } = await octokit.rest.issues.listComments({ owner, repo, issue_number: issueNumber });

    const participants: Set<string> = new Set(comments.map(comment => comment.user.login));
    const issueLink = `https://github.com/${owner}/${repo}/issues/${issueNumber}`;

    return { author, participants, issueLink };
}

async function getPullRequestDetails(owner: string, repo: string, prNumber: number, author: string): Promise<PRDetails> {

    const { data: reviews } = await octokit.rest.pulls.listReviews({ owner, repo, pull_number: prNumber });

    const { data: comments } = await octokit.rest.issues.listComments({ owner, repo, issue_number: prNumber });

    const reviewers: Set<string> = new Set(reviews.map(review => review.user.login));
    const participants: Set<string> = new Set(comments.map(comment => comment.user.login));
    const authors: Set<string> = new Set([author]);
    const prLink = `https://github.com/${owner}/${repo}/pull/${prNumber}`;

    return { authors, reviewers, participants, prLink };
}

async function analyzeRepository(owner: string, repo: string):Promise<GhAnalysisResults> {
    //can i somehow differntiate between merged and closed?
    const prs = await getMergedPullRequests(owner, repo,"closed",null);
    const pr_interactions: PRInteractionsMap = new Map();

    for (const pr of prs) {
        const author: string = pr.user.login;
        const { reviewers, participants, prLink, authors } = await getPullRequestDetails(owner, repo, pr.number, author);

        if (!pr_interactions.has(prLink)) {
            pr_interactions.set(prLink, { authors: new Set(), reviewers: new Set(), participants: new Set(), prLink });
        }
        const pr_interaction = pr_interactions.get(prLink);
        if (!pr_interaction) {continue;}
        pr_interaction.authors.add(author);
        reviewers.forEach(reviewer => pr_interaction.reviewers.add(reviewer));
        participants.forEach(participant => pr_interaction.participants.add(participant));
    }

    const issueInteractions: IssueInteractionsMap = new Map();
    const issues = await getIssues(owner, repo,"closed");
    for (const issue of issues) {
        const issueLink = `https://github.com/${owner}/${repo}/issues/${issue.number}`;
        const author: string = issue.user.login;
        const { participants } = await getIssueDetails(owner, repo, issue.number, author);

        if (!issueInteractions.has(issueLink)) {
            issueInteractions.set(issueLink, { author, participants, issueLink });
        }
    }

    // Print results
    pr_interactions.forEach((data, prKey) => {
        console.log(`PR: ${data.prLink}`);
        console.log(`Authors: ${[...data.authors.values()]}`);
        console.log(`Reviewed By: ${[...data.reviewers.values()]}`);
        console.log(`Participants: ${[...data.participants.values()]}`);
        console.log("------------------");
    });

    // Print Issue results
    issueInteractions.forEach((data, issueLink) => {
        console.log(`Issue: ${data.issueLink}`);
        console.log(`Author: ${data.author}`);
        console.log(`Participants: ${[...data.participants.values()]}`);
        console.log("------------------");
    });

    return {pr_results:pr_interactions,issues_results:issueInteractions}
}






console.log(result)









