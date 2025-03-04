import "dotenv/config"
import {Octokit} from "octokit";
import commandLineArgs from "command-line-args"
import "node:https"
import "node:fs"
import * as fs from "node:fs";
import assert = require("node:assert");
interface CliOptions {
    query?:String,
    keywords?: string[],
    num_top_packages?: number,
    popularity_weight?: number,
    quality_weight?: number,
    maintenance_weight?: number,
}

interface GhAnalysisResults {
    pr_results:PRInteractionsMap,
    issues_results:IssueInteractionsMap
}

type PackageLinks = {
    npm: string;
    homepage?: string;
    repository?: string;
    bugs?: string;
};

type Author = {
    name: string;
};

type Publisher = {
    username: string;
    email: string;
};

type Maintainer = {
    username: string;
    email: string;
};

type PackageScoreDetail = {
    quality: number;
    popularity: number;
    maintenance: number;
};

type PackageScore = {
    final: number;
    detail: PackageScoreDetail;
};

type NpmsPackage = {
    name: string;
    scope: string;
    version: string;
    description: string;
    keywords?: string[];
    date: string; // ISO 8601 date string
    links: PackageLinks;
    author?: Author;
    publisher: Publisher;
    maintainers: Maintainer[];
};

type SearchResult = {
    package: NpmsPackage;
    score: PackageScore;
    searchScore: number;
};

type NpmsSearchResponse = {
    total: number;
    results: SearchResult[];
};

console.log("Checking if GITHUB_API_KEY variable is set");
if (!process.env.GITHUB_API_KEY) {
    console.log("Please set GITHUB_API_KEY to continue");
    process.exit(-1);
}
console.log("Progress: GITHUB_API_KEY is set");

const octokit = new Octokit({auth:process.env.GITHUB_API_KEY});

async function getMostPopularFossPackagesFromNPM(options:CliOptions) {
    const npmsIOBaseUrl = new URL("/search", "https://api.npms.io/v2/");
    let finalQuery = options.query;
    if (options.keywords.length > 0) {
        finalQuery += "+keywords:"
        options.keywords.forEach(keyword => {
            finalQuery += keyword + ','
        })
        //remove the last comma
        finalQuery = finalQuery.substring(0, finalQuery.length - 1);
    }

    if (options.popularity_weight) {
        finalQuery += "+popularity_weight:" + options.popularity_weight;
    }
    if (options.quality_weight) {
        finalQuery += "+quality_weight:" + options.quality_weight;
    }

    if (options.maintenance_weight) {
        finalQuery += "+maintenance_weight:" + options.maintenance_weight;
    }

    npmsIOBaseUrl.searchParams.set("q", encodeURIComponent(finalQuery.toString()));
    //The total number of results to return (max of 250)
    // Default value: 25
    npmsIOBaseUrl.searchParams.set("size", encodeURIComponent(options.num_top_packages));
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
        name:"num-top-packages",alias:"n",type:Number,defaultValue:50
    },
    {
        name:"popularity-weight",alias:"pw",type:Number,defaultValue:100
    },
    {
        name:"quality_weight",alias:"qw",type:Number,defaultValue: 2
    },
    {
        name:"maintenance_weight",alias:"mw",type:Number,defaultValue:5
    }
]

function getUserInput() {
    const options = commandLineArgs(cliOptions) as CliOptions
    return options
}

function persistResultToStorage(r:GhAnalysisResults) : GhAnalysisResults {
    console.log(r);
    //persist to db or something
    return r
}

const userQuery = getUserInput();
const result = await getMostPopularFossPackagesFromNPM(userQuery);
const body = await result.json() as NpmsSearchResponse;
const githubRepos = body.results
    .filter(s=> s.package.links.repository !== undefined &&
    s.package.links.repository !== null &&
    s.package.links.repository.startsWith("https://github.com"))
    .map(s=>s.package.links.repository)
    .map(url => new URL(url))
    .map(extractOwnerAndRepoNameFromUrl)
    .map(ghInfo => await analyzeRepository(ghInfo.owner,ghInfo.repo))
    .map(persistResultToStorage)





function extractOwnerAndRepoNameFromUrl(url:URL) {
    const splitted_paths = url.pathname.split("/")
    return {owner:splitted_paths[1],repo:splitted_paths[2]}
}




type PRDetails = {
    authors: Set<string>;
    reviewers: Set<string>;
    participants: Set<string>;
    prLink: string;
};
type IssueDetails = {
    author: string;
    participants: Set<string>;
    issueLink: string;
};
type PRInteractionsMap = Map<string, PRDetails>;
type IssueInteractionsMap = Map<string,IssueDetails>;


type PRState = "closed" | "open" | "all"

async function getMergedPullRequests(owner: string, repo: string,state:PRState) {
    assert(state != null)
    const { data: pullRequests } = await octokit.pulls.list({
        owner,
        repo,
        state,
        per_page: 50 // Adjust as needed, max 100 per page
    });

    return pullRequests.filter(pr => pr.merged_at);
}

async function getPullRequestDetails(owner: string, repo: string, prNumber: number, author: string): Promise<PRDetails> {
    const { data: reviews } = await octokit.pulls.listReviews({ owner, repo, pull_number: prNumber });
    const { data: comments } = await octokit.issues.listComments({ owner, repo, issue_number: prNumber });

    const reviewers: Set<string> = new Set(reviews.map(review => review.user.login));
    const participants: Set<string> = new Set(comments.map(comment => comment.user.login));
    const authors: Set<string> = new Set([author]);
    const prLink = `https://github.com/${owner}/${repo}/pull/${prNumber}`;

    return { authors, reviewers, participants, prLink };
}

async function analyzeRepository(owner: string, repo: string):Promise<GhAnalysisResults> {
    const prs = await getMergedPullRequests(owner, repo,"closed");
    const pr_interactions: PRInteractionsMap = new Map();
    const issues_interactions: IssueInteractionsMap = new Map();

    for (const pr of prs) {
        const author: string = pr.user.login;
        const { reviewers, participants, prLink, authors } = await getPullRequestDetails(owner, repo, pr.number, author);

        if (!pr_interactions.has(prLink)) {
            pr_interactions.set(prLink, { authors: new Set(), reviewers: new Set(), participants: new Set(), prLink });
        }

        pr_interactions.get(prLink)?.authors.add(author);
        reviewers.forEach(reviewer => pr_interactions.get(prLink)?.reviewers.add(reviewer));
        participants.forEach(participant => pr_interactions.get(prLink)?.participants.add(participant));
    }

    // Print results
    pr_interactions.forEach((data, prKey) => {
        console.log(`PR: ${data.prLink}`);
        console.log(`Authors: ${data.authors}`);
        console.log(`Reviewed By: ${data.reviewers}`);
        console.log(`Participants: ${data.participants}`);
        console.log("------------------");
    });
    return {pr_results:pr_interactions,issues_results:issues_interactions}
}






console.log(result)









