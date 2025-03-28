import sqlite3 from "sqlite3"
import dotenv from "dotenv"
import {GhAnalysisResults} from "./types";
import {getRepoFromPrLink} from "./utils";
const sqlitedb = sqlite3.verbose()
const db = new sqlitedb.Database(`github-data-latest.db` )
dotenv.config()
console.log("Creating tables of sqlite db")
db.run(`CREATE TABLE IF NOT EXISTS gh_users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE
    );`)

db.run(`CREATE TABLE IF NOT EXISTS pull_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pr_link TEXT UNIQUE,
        repo TEXT,
        author_id INTEGER,
        FOREIGN KEY (author_id) REFERENCES gh_users(id)
    );`)

db.run(`CREATE TABLE IF NOT EXISTS pr_review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pr_id INTEGER,
        reviewer_id INTEGER,
        FOREIGN KEY (pr_id) REFERENCES pull_requests(id),
        FOREIGN KEY (reviewer_id) REFERENCES gh_users(id)
    );`)
console.log("creating of tables was completed")
db.run(`CREATE INDEX IF NOT EXISTS idx_pr_author ON pull_requests(author_id);`)

db.run(`CREATE INDEX IF NOT EXISTS idx_review_reviewer ON pr_review(reviewer_id);`)

db.run(`CREATE INDEX IF NOT EXISTS idx_pr_repo ON pull_requests(repo);`)
console.log("creating of indexes was completed")

// Promisify database methods
const dbRun = (sql: string, params: any[] = []): Promise<{ lastID: number }> =>
    new Promise((resolve, reject) => {
        db.run(sql, params, function(err) {
            if (err) reject(err);
            else resolve({ lastID: this.lastID });
        });
    });

const dbGet = (sql: string, params: any[] = []): Promise<any> =>
    new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => {
            if (err) reject(err);
            else resolve(row);
        });
    });
async function getOrCreateUser(username: string): Promise<number> {
    const existingUser = await dbGet('SELECT id FROM gh_users WHERE username = ?', [username]);
    if (existingUser) return existingUser.id;

    const result = await dbRun('INSERT INTO gh_users (username) VALUES (?)', [username]);
    return result.lastID;
}

async function getOrCreatePR(prLink: string, repo: string, authorId: number): Promise<number> {
    const existingPR = await dbGet('SELECT id FROM pull_requests WHERE pr_link = ?', [prLink]);
    if (existingPR) return existingPR.id;

    const result = await dbRun(
        `INSERT INTO pull_requests (pr_link, repo, author_id) VALUES (?, ?, ?);`,
        [prLink, repo, authorId]
    );
    return result.lastID;
}

async function addReview(prId: number, reviewerId: number): Promise<void> {
    const existingReview = await dbGet(
        'SELECT id FROM pr_review WHERE pr_id = ? AND reviewer_id = ?',
        [prId, reviewerId]
    );
    if (!existingReview) {
        await dbRun('INSERT INTO pr_review (pr_id, reviewer_id) VALUES (?, ?)', [prId, reviewerId]);
    }
}


async function persistResultToStorage(r: GhAnalysisResults): Promise<GhAnalysisResults> {
    // @ts-ignore
    for (const [prUrl, prDetails] of r.pr_results.entries()) {
        try {
            await dbRun('BEGIN TRANSACTION');

            const prLink = prDetails.prLink;

            // Handle authors
            if (prDetails.authors.size === 0) {
                console.error(`Skipping PR ${prLink} - no authors found`);
                await dbRun('ROLLBACK');
                continue;
            }
            const firstAuthor = prDetails.authors.values().next().value;
            const authorId = await getOrCreateUser(firstAuthor);

            // Extract repo from PR link
            let repo: string;
            try {
                repo = getRepoFromPrLink(prLink);
            } catch (e) {
                console.error(`Skipping PR ${prLink}: ${e.message}`);
                await dbRun('ROLLBACK');
                continue;
            }

            // Handle PR
            const prId = await getOrCreatePR(prLink, repo, authorId);

            // Handle reviewers
            for (const reviewer of prDetails.reviewers) {
                const reviewerId = await getOrCreateUser(reviewer);
                await addReview(prId, reviewerId);
            }

            await dbRun('COMMIT');
        } catch (e) {
            console.error(`Failed to process PR ${prUrl}:`, e);
            await dbRun('ROLLBACK');
        }
    }

    console.log('Persisted PR data to database. Note: Issue data is not stored in current schema.');
    return r;
}

async function repoExists(owner:string, repo:string):Promise<boolean> {
    try {
        const query = `SELECT EXISTS(SELECT 1 from pull_requests where repo='${owner}/${repo}') as repo_exists;`;
        const result = await dbGet(query,[])
        return result["repo_exists"]
    } catch (e) {
        console.log(`While checking if repo ${owner}/${repo} exists got an error from db: ${e}`)
        return false;
    }

}



export {dbGet,dbRun,db,getOrCreateUser,getOrCreatePR,addReview,persistResultToStorage,repoExists}