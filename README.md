# Markovian-Session-Measures
A Markovian Approach to Evaluate Session-based IR Systems

We investigate a new approach for evaluating session-based
information retrieval systems, based on Markov chains. In particular, we
develop a new family of evaluation measures, inspired by random walks,
which account for the probability of moving to the next and previous
documents in a result list, to the next query in a session, and to the
end of the session. We leverage this Markov chain to substitute what in
existing measures is a fixed discount linked to the rank of a document or
to the position of a query in a session with a stochastic average time to
reach a document and the probability of actually reaching a given query.
We experimentally compare our new family of measures with existing
measures - namely, session DCG, Cube Test, and Expected Utility -
over the TREC Dynamic Domain track, showing the  flexibility of the 
proposed measures and the transparency in modeling the user dynamics.


### What is this repository for? ###
This repository contains the Experiments Code for the paper:<br/>
**A Markovian Approach to Evaluate Session-based IR Systems**<br/>
van Dijk, D., Ferrante, M., Ferro, N., and Kanoulas, E. (2019)<br/>
Int. Conference Paper In Fuhr, N., Mayr, P., Azzopardi, L., Stein, B., Hauff, C., and Hiemstra, D.<br/>
, editors, Advances in Information Retrieval. Proc. 41st European Conference on IR Research<br/>
(ECIR 2019). Lecture Notes in Computer Science (LNCS), Springer, Heidelberg, Germany

### Code ###
The code is written for Python 3.5  

dependencies:  
oct2py 4.0.6

The code for scoring session DCG, Cube Test, and Expected Utility is  based on code from 
the Dynamic Domain Track:  
https://github.com/trec-dd/trec-dd-jig  


### Data ###
Dynamic Domain tracks 2015/2016: 
www.trec-dd.org

### Setup ###
Code and run scripts are divided into the following folders: 
- matlab_msm    (MsM measures)  
- msm_scoring   (Score MsM configurations)  
- scoring       (Score runs/generate data for MsM measures) 

### Who do I talk to? ###
David van Dijk <d.v.van.dijk@hva.nl><br/>
Marco Ferrante <ferrante@math.unipd.it><br/>
Nicola Ferro <ferro@dei.unipd.it><br/>
Evangelos Kanoulas <e.kanoulas@uva.nl><br/>
