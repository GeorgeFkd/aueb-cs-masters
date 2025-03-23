import {IssueDetails, PRDetails, PRState} from "./types";
import {Octokit} from "octokit";
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
async function getPullRequestDetails(owner: string, repo: string, prNumber: number, author: string): Promise<PRDetails> {

    const { data: reviews } = await octokit.rest.pulls.listReviews({ owner, repo, pull_number: prNumber });

    const { data: comments } = await octokit.rest.issues.listComments({ owner, repo, issue_number: prNumber });

    const reviewers: Set<string> = new Set(reviews.filter(review=> review.user && review.user.login).map(review => review.user.login));
    const participants: Set<string> = new Set(comments.filter(review=> review.user && review.user.login).map(comment => comment.user.login));
    const authors: Set<string> = new Set([author]);
    const prLink = `https://github.com/${owner}/${repo}/pull/${prNumber}`;

    return { authors, reviewers, participants, prLink };
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


async function getMergedPullRequests(owner: string, repo: string,state:PRState,page: number | null) {
    // assert(state != null)
    const { data: pullRequests } = await octokit.rest.pulls.list({
        owner,
        repo,
        state,
        per_page: 100, // Adjust as needed, max 100 per page
        page:page || 1
    });

    return pullRequests.filter(pr => pr.merged_at);
}

export {getIssues,getMergedPullRequests,getPullRequestDetails,getIssueDetails}