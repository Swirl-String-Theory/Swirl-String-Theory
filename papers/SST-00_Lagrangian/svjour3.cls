%% This is a placeholder for svjour3.cls.
%% For full functionality, please download the official Springer version.
%% This version allows basic LaTeX compilation.

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{svjour3}[2010/03/15 Springer Journal Class]

\LoadClass[11pt]{article}

\RequirePackage{amssymb}
\RequirePackage{amsmath}
\RequirePackage{graphicx}
\RequirePackage{float}
\RequirePackage{hyperref}

% Define dummy journalname command
\newcommand{\journalname}[1]{}

% Smart qed environment
\newcommand{\smartqed}{\let\qed=\relax}

% Dummy maketitle commands
\renewcommand{\maketitle}{%
    \begin{center}
    {\LARGE \@title \par}
    \vskip 1em
        {\large \@author \par}
    \vskip 1em
    \@date
    \end{center}
    \vskip 2em
}

\newcommand{\institute}[1]{}
\renewcommand{\author}[1]{\def\@author{#1}}
\renewcommand{\title}[1]{\def\@title{#1}}
\renewcommand{\date}[1]{\def\@date{#1}}

% Keywords
\newcommand{\keywords}[1]{\par\noindent{\bf Keywords:} #1}

\endinput