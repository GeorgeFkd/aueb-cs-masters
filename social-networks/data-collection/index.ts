import dotenv from "dotenv"
import commandLineArgs from "command-line-args"
import "node:https"
import "node:fs"
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

import {persistResultToStorage,repoExists} from "./db";
import {extractOwnerAndRepoNameFromUrl} from "./utils";
import {getIssueDetails, getIssues, getMergedPullRequests, getPullRequestDetails} from "./github";
dotenv.config()

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
        name:"query", alias:"q",type:String,defaultValue:"vue"
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
console.log("The total packages fetched are: ",body.total)
console.log("The total packages remaining are: ",githubRepos.length)



let failedRepos = []
for (const repo of githubRepos) {
    try {
        const repoUrl = repo.package.links.repository;
        const timerID = `github-repo-processing:${repoUrl}`
        console.log("Processing: ",repoUrl)
        console.time(timerID)
        const parsedUrl = new URL(repoUrl);
        const ghInfo = extractOwnerAndRepoNameFromUrl(parsedUrl);
        const repoInDb = await repoExists(ghInfo.owner,ghInfo.repo)
        if (repoInDb) {
            console.log(`Skipping ${ghInfo.owner}/${ghInfo.repo}`);
            continue;
        }
        console.log("Repository Analysis")
        const PAGES_OF_MERGE_REQUESTS = 3;
        for(let i=0; i < PAGES_OF_MERGE_REQUESTS; i++) {
            const analysisResult = await analyzeRepository(ghInfo.owner, ghInfo.repo,i);
            console.log("Persisting results to db for page: ",i)
            await persistResultToStorage(analysisResult);
        }

        console.timeEnd(timerID)
    } catch (error) {
        console.error(`Failed to process repository ${repo.package.links.repository}:`, error);
        failedRepos.push(repo);
    }
}

async function analyzeRepository(owner: string, repo: string,page:number):Promise<GhAnalysisResults> {
    //can i somehow differentiate between merged and closed?
    //each page is 100 merged PRs

    const DEBUG_FLAG = true;
    let pr_interactions: PRInteractionsMap = new Map();
    let issueInteractions: IssueInteractionsMap = new Map();

    const prs = await getMergedPullRequests(owner, repo, "closed", page);
    for (const pr of prs) {
        const author: string = pr.user.login;
        const {
            reviewers,
            participants,
            prLink,
            authors
        } = await getPullRequestDetails(owner, repo, pr.number, author);


        if (!pr_interactions.has(prLink)) {
            pr_interactions.set(prLink, {
                authors: new Set(),
                reviewers: new Set(),
                participants: new Set(),
                prLink
            });
        }
        const pr_interaction = pr_interactions.get(prLink);
        if (!pr_interaction) {
            continue;
        }
        pr_interaction.authors.add(author);
        reviewers.forEach(reviewer => pr_interaction.reviewers.add(reviewer));
        participants.forEach(participant => pr_interaction.participants.add(participant));
    }


    const issues = await getIssues(owner, repo, "closed");
    for (const issue of issues) {
        const issueLink = `https://github.com/${owner}/${repo}/issues/${issue.number}`;
        const author: string = issue.user.login;
        const {participants} = await getIssueDetails(owner, repo, issue.number, author);

        if (!issueInteractions.has(issueLink)) {
            issueInteractions.set(issueLink, {author, participants, issueLink});
        }
    }

    if (DEBUG_FLAG) {
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
    }


    return {pr_results:pr_interactions,issues_results:issueInteractions}
}

