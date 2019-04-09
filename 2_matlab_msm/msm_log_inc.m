%% msm
%
% Computes the MsM measure for a search session.

%% Synopsis
%
%   [m] = msm(run, p, q, r, s)
%
% *Parameters*
%
% * *|run|* - the run to be evaluated. A run is a N x K integer matrix
% where rows a documents, columns are queries, and each cell contains a
% natural number representing the relevance of a document.
% * *|p|* - the probability of moving forward from a document to the next
% one within a query. It must be greater than zero.
% * *|q|* - the probability of moving backward from a document to the
% previous one within a query.
% * *|r|* - the probability of jumping to the first document of the next
% query. It must be greater than zero.
% * *|s|* - the probability of stopping a search session. It must be
% greater than zero.
%
% *Returns*
%
% * *|m|* - the MsM measure for the given run.


%% Information
%
% * *Author*: <mailto:ferro@dei.unipd.it Nicola Ferro>
% * *Version*: 1.00
% * *Since*: 1.00
% * *Requirements*: Matlab 2017a or higher
% * *Copyright:* (C) 2018 <http://ims.dei.unipd.it/ Information
% Management Systems> (IMS) research group, <http://www.dei.unipd.it/
% Department of Information Engineering> (DEI), <http://www.unipd.it/
% University of Padua>, Italy
% * *License:* <http://www.apache.org/licenses/LICENSE-2.0 Apache License,
% Version 2.0>

%%
%{
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
      http://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
%}

%%

function [m] = msm_lin(run, p, q, r, s)

    % check the number of input parameters
    narginchk(5, 5);

    % check that run is an integer matrix with values greater than or equal
    % to zero
    validateattributes(run, {'numeric'}, ...
        {'nonempty', 'integer', 'ndims', 2, '>=', 0}, '', 'run');
    
    % check that p is a real scalar with values in (0, 1]
    validateattributes(p, {'numeric'}, ...
        {'nonempty', 'real', 'scalar', '>', 0, '<=', 1}, '', 'p');
    
    % check that q is a real scalar with values in [0, 1]
    validateattributes(q, {'numeric'}, ...
        {'nonempty', 'real', 'scalar', '>=', 0, '<=', 1}, '', 'q');
    
    % check that r is a real scalar with values in (0, 1]
    validateattributes(r, {'numeric'}, ...
        {'nonempty', 'real', 'scalar', '>', 0, '<=', 1}, '', 'r');
    
    % check that s is a real scalar with values in (0, 1]
    validateattributes(s, {'numeric'}, ...
        {'nonempty', 'real', 'scalar', '>', 0, '<=', 1}, '', 's');
    
    % check that p + q + r + s = 1
%    assert( (p + q + r + s == 1), 'p + q + r + s = %4.3f + %4.3f + %4.3f + %4.3f must sum up to %4.3f instead of %4.3f', ...
%        p, q, r, s, 1.0, p + q + r + s);
    
    % the number of retrieved documents for each query
    N = size(run, 1);
    
    % the number of queries in the session
    K = size(run, 2);
    
    % the re-scaled transition probabilities for the first document, for
    % which there is no backward transition probability
    p1 = p/(p+s+r);
    s1 = s/(p+s+r);
    r1 = r/(p+s+r);
    
    % the re-scaled transition probabilities for the last document, for
    % which there is no forward transition probability
    qN = q/(q+s+r);
    sN = s/(q+s+r);
    rN = r/(q+s+r);
    

    % The transition matrix P is a N+2 x N+2 stochastic matrix where:
    % - the N x N submatrix contains the backward and forward transitions
    % between the documents within a query, paying attention to the
    % re-scaled transition probabilities for the first and last document
    % - the additional absorbing state F represents the end of a search
    % session
    % - the additional absorbing state Q represents the jump to the next
    % query
    %
    % Here there is the layout of the transition matrix
    %
    %       |   1      2       3           N-1     N   |   F   |   Q  |
    %       -----------------------------------------------------------
    %   1   |   0      p1      0           0       0   |   s1  |   r1 |
    %   2   |   q      0       p           0       0   |   s   |   r  |
    %   3   |   0      q       0    p      0       0   |   s   |   r  |
    %       |                                                         |
    %       |                                                         |
    %   N-1 |   0      0       0        q  0       p   |   s   |   r  |
    %   N   |   0      0       0           qN      0   |   sN  |   rN |
    %       -----------------------------------------------------------
    %   F   |   0      0       0           0       0   |   1   |   0  |
    %   Q   |   0      0       0           0       0   |   0   |   1  |
    %       -----------------------------------------------------------
    
    % the indices of the F and Q states
    F = N+1;
    Q = N+2;
    
    % create the upper diagonal
    tmp = [p1 repmat(p, 1, N-2)];
    P = diag(tmp, 1);
    
    % add the lower diagonal
    tmp = [repmat(q, 1, N-2) qN];
    P = P + diag(tmp, -1);
    
    % add the F state colum (first N rows of it)
    tmp = [s1 repmat(s, 1, N-2) sN];
    P = [P tmp.'];
    
    % add the Q state colum (first N rows of it)
    tmp = [r1 repmat(r, 1, N-2) rN];
    P = [P tmp.'];
    
    % add the last two rows for the F and Q states
    P = [P; [zeros(2, N) eye(2, 2)]];
    
    % the average time to go from document 1 to document i
    ei = NaN(N, 1);
    
    % the average time to go from document 1 to itself is 0
    ei(1) = 0;
    
    % Phat is the same matrix as P but where the F and Q state rows and
    % columns have been removed since, to compute the average time to move
    % from document 1 to document i, you must assume that neither
    % the search session has ended nor you have moved to the next query
    Phat = P;
    Phat([F Q], :) = [];                          % remove the F and Q columns
    Phat(:, [F Q]) = [];                          % remove the F and Q rows
    Phat = bsxfun(@rdivide, Phat, sum(Phat, 2));  % make it stochastic again
    
    % for each document
    for i = 1:N-1
        
       % Compute the average time to go from each document to document i.
       %
       % Note that, for Matlab, x = A\b is computed differently than
       % x = inv(A)*b and is recommended for solving systems of linear
       % equations, since it is faster and and has less residual error by
       % several orders of magnitude
       tmp = (eye(i, i) - Phat(1:i, 1:i)) \ ones(i, 1);

       % we are interested only in the average time to go from
       % document 1 to document i
       ei(i+1) = tmp(1);
    end % for document
    
    
    % the average time to move to the next query
    eQ = NaN;
    
    % Phat is the same matrix as P but where the F state rows and columns
    % have been removed since, to compute the average time to move to the
    % next query, you must assume the search session has not ended.
    Phat = P;
    Phat(F, :) = [];                              % remove the F column
    Phat(:, F) = [];                              % remove the F row
    Phat = bsxfun(@rdivide, Phat, sum(Phat, 2));  % make it stochastic again
    
    % Compute the average time to go from each document to the next query.
    tmp = (eye(N, N) - Phat(1:N, 1:N)) \ ones(N, 1);
    
    % we are interested only in the the average time to go from document 1
    % to the next query, which is the average time to scan a whole result
    % list and move to the next query
    eQ =  tmp(1);
    
    % the probability to go from document i to state F, i.e. end of search
    % session, in the first K-1 queries
    hF = (eye(N, N) - P(1:N, 1:N)) \ P(1:N, F);
    
    
    % Phat is the same matrix as P but where the Q state rows and columns
    % have been removed since, to compute the probability to go from
    % document i to state F in the K-th query, there is not next query.
    Phat = P;
    Phat(Q, :) = [];                              % remove the Q column
    Phat(:, Q) = [];                              % remove the Q row
    Phat = bsxfun(@rdivide, Phat, sum(Phat, 2));  % make it stochastic again
    
    
    % the probability to go from document i to state F, i.e. end of search
    % session, in the K-th query
    hFK = (eye(N, N) - Phat(1:N, 1:N)) \ Phat(1:N, F);
    
    
    % the probability to go from document 1 (of the first query) to the
    % state F of the j-th query
    hj(1:K-1) = (1 - hF(1)).^(0:K-2)*hF(1);
    hj(K) = (1 - hF(1)).^(K-1)*hFK(1);
    
    % the probability of ending the search session in query j
    tmp = cumsum(hj);
    pj(1) = 1;
    pj(2:K) = 1 - tmp(1:K-1);
    
    
    % discount the gain of each document by the average time needed to
    % reach it.
    %
    % Note that we add 1 to ei to avoid dividing by zero for the first
    % document.
    %
    % N.B. Here we could use other discount functions, such as the log of
    % the average time, and so on
    
    m = run .* (1 + log(1 + repmat(ei, 1, K) + repmat(0:K-1, N, 1)*eQ))

    % compute the overall gain of each query in the session
    m = sum(m);
    
    % weight the gain of each query by the probability of ending the
    % session in that query
    m = sum(pj .* m);
end

