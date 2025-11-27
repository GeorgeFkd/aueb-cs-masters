# aueb-cs-masters

## Courses Completed:
- Algorithms: Design and Analysis
- Blockchain and Smart Contracts
- Reinforcement Learning
- Natural Language Processing
- Research Methodology
- Computer Game Graphics and Virtual Reality
- Research in Computer Science 2
- Social Networks: Theory and Practice
- Cryptography and Applications
- Convex Optimization

## Winter Semester 

### Natural Language Processing(NLP)
Prof. [Ion Androutsopoulos](https://www.aueb.gr/el/faculty_page/%CE%91%CE%BD%CE%B4%CF%81%CE%BF%CF%85%CF%84%CF%83%CE%BF%CF%80%CE%BF%CF%85%CE%BB%CE%BF%CF%82-%CE%99%CF%89%CE%BD-%CE%99%CF%89%CE%B1%CE%BD%CE%BD%CE%B7%CF%82)

Learned about different AI learning models and related concepts and applied them to NLP tasks.
Below is an overview of things we learned:

1. Traditional Language Models(N-grams)
2. Features(TF-IDF,SVD,PMI,K-Means) and Evaluation Metrics
3. Regression (Linear and Multinomial)
4. MLPs with SGD for text classification and token classification(+ different normalisations), Word2Vec
5. RNNs(+Bidirectional and Stacked ones) with GRUs/LSTMs for cells, Self Attention
6. CNNs 
7. Transformers and LLMs
8. Speech recognition basics

#### Exam Style (2024-2025)
Studying the given solved exercises will get you far(the exams do not include anything code related).

In our year it had: Calculations from N-grams, prompt engineering, derivation for backpropagation, Dimensions of layers in a complex model(plenty of examples given from his exercises), the part with BeRT and masking words to make it learn new stuff, MLP as attention head to train an existing model for a given task.

### Blockchains
Prof. [Spyros Voulgaris](https://www.aueb.gr/el/faculty_page/voylgaris-spyridon)

Learned about blockchains and cryptocurrencies in their algorithmic and design level as protocols and systems(no, you will not make money from crypto by taking this course). 

Main topics were **Bitcoin**, **Ethereum**, **Consensus protocols** and communication between different ledgers. 
It was heavy on discussing the design decisions, how incentives work, how the peer to peer nature and decentralisation are achieved through cryptographic tools and distributed protocols. 
We did not get deep into cryptography, only learned some related concepts wherever they were needed.

#### Exam Style (2024-2025)

Questions related to WHY things in blockchains are made that way, why do we need certain things, how could we implement a specific thing using blockchains, what would happen to a system if we removed something etc. etc. 

Ofc you will not write code as part of the exam.

### Reinforcement Learning(RL)
Prof. [Stavros Toumpis](https://www.aueb.gr/el/faculty_page/%CF%84%CE%BF%CF%85%CE%BC%CF%80%CE%B7%CF%83-%CF%83%CF%84%CE%B1%CF%85%CF%81%CE%BF%CF%83)

We followed the book of Sutton and Barton on RL and got up to Q-Learning and n-step bootstrapping.
The things we learned were:

- Dynamic Programming Methods
- Finite Markov Decision Processes
- Monte Carlo Methods
- Temporal Difference Learning (SARSA, Q-Learning)
- N-step bootstrapping


#### Exam Style (2024-2025)
Exercises from the book itself, nothing more. Properly studying from the book should be enough(working out proofs and doing the exercises).

### Design and Analysis of Algorithms
Prof. [Markakis](https://www.aueb.gr/el/faculty_page/%CE%BC%CE%B1%CF%81%CE%BA%CE%B1%CE%BA%CE%B7%CF%83-%CE%B5%CF%85%CE%B1%CE%B3%CE%B3%CE%B5%CE%BB%CE%BF%CF%83)
Great course, helpful for really diving deeper into algorithms and should help with LeetCode style 
problems as you get to use each problem-solving methodology on different problems(but only write pseudocode,
if you are interested implement them in actual code).

Topics:

Different Methodologies and Design Strategies for Algorithms, mixed with a bit of theory related to algorithms. 

- Divide and Conquer, Greedy and Dynamic Programming
- Graph Algorithms(+Flows and Matchings)
- P,NP,reductions, and approximation algorithms
- Tackling NP problems (TSP,Set Cover,Vertex Cover, Subset Sum, Job Scheduling, Knapsack)
- Bits of Linear and Integer Programming (and how we can use them to create algorithms)
- Randomised Algorithms

#### Exam Style (2024-2025)
Exercises like the ones in the assignments, they are tough because the time is limited, you need to get them right the first time eyou will not have time to revisit things. 
Focus on solving problems not just reading the theory (also remember all the problems
and their formulations, it is useful.).

---

## Spring Semester

### Convex Optimisation
Prof. G. Amanatidis

Tough maths course, it starts with the fundamentals about convexity and builds up to understanding why the Langrangian method works and optimisation algorithms such interior point methods and gradient descent. Not recommended for people without a sturdy mathematical background, mostly Linear Algebra is needed and a general mathematical background (if you are not used to doing proofs yourself this will be a tough course). You need to attend this otherwise you will be in a tough spot. Also there are stanford youtube videos from the guy that wrote the book used in this course so that's a plus. NO YOU CANNOT CRAM THIS COURSE, IT NEEDS TIME TO REALLY SETTLE IN AS KNOWLEDGE. The professor is really understanding that this is a CS department and not a maths department so he makes things definitely easier and explains thoroughly. 

It had 5 sets of exercises from the book, Convex Optimisation of S.Boyd, that was generally followed in the whole course, while skipping certain niche topics.

#### Exam Style (2024-2025)
The exams were similar to things he had already shown in class, so any problem done in class or as part of homework and then discussed in class, should be properly studied. Bits of everything nothing was really skipped. For us the material for the exam was up to chapter 5 with some things skipped.




### Game Graphics and VR
Prof. [G. Papaioannou](https://www.aueb.gr/el/faculty_page/%CF%80%CE%B1%CF%80%CE%B1%CF%8A%CF%89%CE%B1%CE%BD%CE%BD%CE%BF%CF%85-%CE%B3%CE%B5%CF%89%CF%81%CE%B3%CE%B9%CE%BF%CF%83)

Great course, do not expect fluffy gaming stuff and all that. This is applying maths, mostly Linear Algebra and bits of statistics, to make games. You will understand how 2D and 3D games work, how lighting and shadows are implemented in games and various algorithms used. There is also a big project where you can make a game either using an engine or just C++ and OpenGL. You need to attend this course and give attention as the slides provided are not that enlightening and you will have to figure out many things yourself. It is a bit overwhelming in the beginning as he tends to go fast, but attending will help you in the long run. 

#### Exam Style (2024-2025)
Simple questions regarding explaining how something works, or pictures to tell him what technique was used. Also culling as a technique which types of it apply better to a specific scenario given. Not math related things, more on the graphics side, what advantages disadvantages algorithms have, where are techniques used, how to achieve a certain result, how to fix artifacts etc. etc.

### Cryptography and Applications
Prof. G. Patsakis

This is a great course to brush up on fundamentals of cryptography and security(it helped me immensely as somebody that did not have a dedicated cryptography course in BSc). The prof really conveys the mindset of security and how things work practically. It is not an overly mathy course, just some simple number theory he does not dive deep into weird math concepts. Attend because the prof. is really fun and his teaching is really engaging. 

#### Exam Style (2024-2025)
Basically from a platform called CryptoHack he told us to score 1000 points for the 10/10, and also write a report on the things we solved. The report matters, i probably lost 1.5 grades bcs I did a terrible job there. Start it early and enjoy it, the courses themselves and the easy questions give around 750 points, enough for a passing grade.

### Social-Networks
Prof. [Katia Papakonstantinopoulou](https://www2.aueb.gr/users/katia/)

This is a course where social networks/graphs are studied using a variety of techniques. It starts off with simple graph theory stuff and builds up to Graph Neural Networks in the end. This is a course on the easier side of things compared to the rest. It is recommended to not have yourself be overwhelmed by the level of difficulty of the rest of the programme. You will get a revision of graph related things and learn some cool new concepts, and how things work like PageRank and Social Media recommendations etc. etc.. It had one project that was basically applying the material to a dataset and writing a report about it(think of it like a beginner level paper, thats how i wrote it).

#### Exam Style (2024-2025)
We discussed it with the prof. and we actually did a presentation on a relevant paper of our choice(checked by her ofc) as the exam. You can discuss this with her as the exams coming up she doesn't have a problem with it. The grade was 50/50, project/presentation. 






