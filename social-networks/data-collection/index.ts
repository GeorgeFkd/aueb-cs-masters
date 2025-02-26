import "dotenv/config"
import {Octokit} from "octokit";
import "node:https"
import "node:fs"
import * as fs from "node:fs";

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

// const octokit = new Octokit({auth:process.env.GITHUB_API_KEY});
// const {
//   data: { login },
// } = await octokit.rest.users.getAuthenticated();

async function getMostPopularFossPackagesFromNPM(q: string, size: number, options?: {
    keywords: string[],
    popularity_weight: number,
    quality_weight: number,
    maintenance_weight: number
} | null) {
    const npmsIOBaseUrl = new URL("/search", "https://api.npms.io/v2/");
    let final_query = q;
    if (options.keywords.length > 0) {
        final_query += "+keywords:"
        options.keywords.forEach(keyword => {
            final_query += keyword + ','
        })
        //remove the last comma
        final_query = final_query.substring(0, final_query.length - 1);
    }

    if (options.popularity_weight) {
        final_query += "+popularity_weight:" + options.popularity_weight;
    }
    if (options.quality_weight) {
        final_query += "+quality_weight:" + options.quality_weight;
    }

    if (options.maintenance_weight) {
        final_query += "+maintenance_weight:" + options.maintenance_weight;
    }

    npmsIOBaseUrl.searchParams.set("q", encodeURIComponent(q));
    //The total number of results to return (max of 250)
    // Default value: 25
    npmsIOBaseUrl.searchParams.set("size", encodeURIComponent(size));
    return await fetch(npmsIOBaseUrl)
}


async function StoreGithubReposOfTopNPMPackages() {
    const result = await getMostPopularFossPackagesFromNPM("react", 50, {
        keywords: [],
        popularity_weight: 100,
        maintenance_weight: 5,
        quality_weight: 2
    })
    console.log(result)

    const result_filename = "npms-io-data.csv"


    const body = await result.json() as NpmsSearchResponse;
    const packages = body.results.map(b => b.package)

    fs.appendFile(result_filename, "Package,Description,Author,Maintainers,Github Repository\n", function (err) {
        if (err) {
            console.log(err);
            throw err;
        }
        console.log("Progress: Headers added to csv")
    })

    const total = packages.length
    let counter = 1;
    for (let p of packages) {
        console.log(p)
        const maintainers = p.maintainers.map(m => m.username).reduce((a, b) => a + "-" + b);
        if (!p.links.repository) {
            continue;
        }
        if (!p.links.repository.startsWith("https://github.com")) continue;
        if (!p.author) {
            continue;
        }
        if (!p.author.name) {
            continue;
        }
        //rm new lines from desc and commas
        const clean_description = p.description.replace(",", " ").replace("\n", " ")
        const package_data = `${p.name},${clean_description},${p.author.name},${maintainers},${p.links.repository}\n`
        const progress_msg = `Progress: ${counter}/${total}`
        fs.appendFile(result_filename, package_data, function (err) {
            if (err) {
                console.log(err);
                throw err;
            }
            console.log(progress_msg)
        })
        counter++;
    }

    console.log(body);
}

await StoreGithubReposOfTopNPMPackages()








