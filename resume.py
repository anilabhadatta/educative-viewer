from flask import flash
from datetime import datetime


def create_resume(username, dic):
    if len(dic.keys()) == 7:
        flash('Cannot create Resume, Please Fill Your Details First', 'danger')
        return False
    res = resume_template(dic)
    with open(f'./portfolio-resume-builder/resume/{username}/resume.tex', 'w') as f:
        f.write(res)
    return True


def resume_template(dic):

    base = r"""
    \documentclass[11pt,a4paper]{article}
    \usepackage{latexsym}
    \usepackage[empty]{fullpage}
    \usepackage{titlesec}
    \usepackage{enumitem}
    \usepackage[hidelinks]{hyperref}
    \usepackage{fontawesome5}
    \usepackage{soul}
    \input{glyphtounicode}
    \RequirePackage{tikz}

    % Adjust margins
    \addtolength{\oddsidemargin}{-0.6in}
    \addtolength{\evensidemargin}{-0.5in}
    \addtolength{\textwidth}{1.19in}
    \addtolength{\topmargin}{-.7in}
    \addtolength{\textheight}{1.4in}
    \setlength{\columnsep}{-1pt}
    \raggedbottom
    \raggedright

    % Sections formatting
    \titleformat{\section}{
    \vspace{-4pt}\scshape\raggedright\large\bfseries
    }{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

    % Ensure that generate pdf is machine readable/ATS parsable
    \pdfgentounicode=1

    %-------------------------
    % Custom commands
    \newcommand{\resumeItem}[1]{
    \item\small{
        {#1 \vspace{-2pt}}
    }
    }

    \newcommand{\resumeSubheading}[4]{
    \vspace{-2pt}\item
        \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
        \textbf{\large#1} & \textbf{\small #2} \\
        \textit{\large#3} & \textit{\small #4} \\
        
        \end{tabular*}\vspace{-7pt}
    }

    \newcommand{\resumeProjectHeading}[2]{
        \item
        \begin{tabular*}{1.001\textwidth}{l@{\extracolsep{\fill}}r}
        \small#1 & \textbf{\small #2}\\
        \end{tabular*}\vspace{-7pt}
    }

    \renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}
    \newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.0in, label={}]}
    \newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
    \newcommand{\resumeItemListStart}{\begin{itemize}}
    \newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}
    \newcommand\sbullet[1][.5]{\mathbin{\vcenter{\hbox{\scalebox{#1}{$\bullet$}}}}}

    %-------------------------------------------
    %%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%
    \usepackage{hyperref}
    """

    linkedin_url = dic['linkedin']
    if len(linkedin_url) > 0:
        linkedin_url = linkedin_url.split('/')[-2]
    heading = rf"""
    \hypersetup{{pdfauthor = PORTFOLIO RESUME BUILDER,
                pdftitle = {dic['full_name']}'s Resume}}
    \begin{{document}}
    
    %----------HEADING----------
    \begin{{center}}

        {{\Huge \scshape {dic['full_name']}}}\\ \vspace{{3pt}}
        \small \href{{tel:{dic['phone_number']}}}{{ \raisebox{{-0.1\height}}\faPhone\ \underline{{{dic['phone_number']}}} ~}} \href{{mailto:{dic['email']}}}{{\raisebox{{-0.2\height}}\faEnvelope\  \underline{{{dic['email']}}}}} ~ \\\vspace{{3pt}}
        \href{{{dic['linkedin']}}}{{\raisebox{{-0.2\height}}\faLinkedin\ \underline{{{linkedin_url}}}}}  ~
        \href{{{dic['github']}}}{{\raisebox{{-0.2\height}}\faGithub\ \underline{{{dic['github'].split('/')[-1]}}}}} ~
        \vspace{{-5pt}}
    \end{{center}}

    """

    education = rf"""
    %-----------EDUCATION-----------
    \section{{EDUCATION}}
    \vspace{{6pt}}
    \resumeSubHeadingListStart
        \resumeSubheading
        {{{dic['college']}}}{{{format_date(dic['college_start'])} -- {format_date(dic['college_end'])}}}
        {{{dic['degree']}  - \textbf{{CGPA}} - \textbf{{{dic['cgpa']}}}}}

        \resumeSubheading
        {{{dic['school']}}}{{{format_date(dic['school_start'])} -- {format_date(dic['school_end'])}}}
        {{{dic['board']}  - \textbf{{Percentage}} - \textbf{{{dic['percentage']}\%}}}}
    \resumeSubHeadingListEnd
    \vspace{{-3pt}}
    """

    programming_skills = rf"""
        %-----------PROGRAMMING SKILLS-----------
        \section{{TECHNICAL SKILLS}}
        \vspace{{6pt}}
        \begin{{itemize}}[leftmargin=0.15in, label={{}}]
            \small{{\item{{
            \textbf{{\normalsize{{Languages:}}}}{{ \normalsize{{{dic['languages']}}}}} \\
            \vspace{{2pt}}
            \textbf{{\normalsize{{Developer Tools:}}}}{{ \normalsize{{{dic['dev_tools']}}}}} \\
            \vspace{{2pt}}
            \textbf{{\normalsize{{Technologies/Frameworks:}}}}{{  \normalsize{{{dic['frameworks']}}}}} \\
            }}}}
        \end{{itemize}}
        \vspace{{-15pt}}
     """

    coding_profile = rf""" 
        %-----------CODING PROFILE---------------
            \section{{CODING PROFILES}}

                \begin{{center}}
                \vspace{{10pt}}
                    \href{{{dic['leetcode']}}}{{\raisebox{{-0.2\height}}\faPoll\ {{Leetcode}}}}\hspace{{4px}}
                    \href{{{dic['codeforces']}}}{{\raisebox{{-0.2\height}}\faPoll\ {{Codeforces}}}}\hspace{{4px}}
                    \href{{{dic['codechef']}}}{{\raisebox{{-0.2\height}}\faPoll\ {{Codechef}}}}
                    \end{{center}}
            \vspace{{-11pt}}
     """
    achievements_string = create_bullet_points(dic['achievements'])
    achievements = rf"""
     %-----------ACHIEVEMENTS---------------
        \section{{ACHIEVEMENTS}}
        \vspace{{6pt}}
        {achievements_string}
        \end{{document}}
     """

    projects_list = dic['projects_data']
    projects_string = rf""
    for i in range(0, len(projects_list), 6):
        projects_string += rf"""
                \resumeProjectHeading
                {{\href{{{projects_list[i+2]}}}{{\textbf{{\normalsize{{\setul{{3pt}}{{.4pt}}\ul{{{projects_list[i]}}}}}}}}} $|$ \normalsize{{\textit{{{{{projects_list[i+1]}}}}}}}}}{{{format_date(projects_list[i+4])} -- {format_date(projects_list[i+5]) if len(projects_list[i+5]) > 0 else 'Present'}}}
                \resumeItemListStart
                \vspace{{10pt}}
                    {create_bullet_points(projects_list[i+3])}
                \resumeItemListEnd 
                \vspace{{-13pt}}
        """
    projects = rf"""
                %-----------PROJECTS-----------
            \section{{PROJECTS}}
                \resumeSubHeadingListStart
                {projects_string}
                \resumeSubHeadingListEnd
            \vspace{{1pt}}
    """

    experience_list = dic['experience_data']
    experience_string = rf""
    for i in range(0, len(experience_list), 6):
        experience_string += rf"""
            \resumeSubheading
            {{{experience_list[i]}}}{{{format_date(experience_list[i+4])} -- {format_date(experience_list[i+5]) if len(experience_list[i+5]) > 0 else 'Present'}}}
            {{\textit{{{experience_list[i+1]}}}}}{{\vspace{{2pt}}}}
            \resumeItemListStart
            \vspace{{5pt}}
                {create_bullet_points(experience_list[i+3])}
                {create_bullet_points(experience_list[i+2], True) if experience_list[i+2] != ''  else ''}  
            \resumeItemListEnd
            \vspace{{3pt}}
        
        """
    experience = rf"""
    % -----------EXPERIENCE-----------
    \section{{EXPERIENCES}}
    \resumeSubHeadingListStart
    \vspace{{6pt}}
        {experience_string}
    \resumeSubHeadingListEnd
    \vspace{{-17pt}}
    """
    return base + heading + education + experience + projects + programming_skills + coding_profile + achievements


def create_bullet_points(string, tech_stack=False):
    string_list = string.split('\n')
    res_string = rf""
    for strings in string_list:
        res_string += rf"""
        $\sbullet[.75] \hspace{{0.2cm}}${{{"Tech Stacks: " if tech_stack else ""}{strings}}} \hspace{{1cm}}\\
        """
    return res_string


def format_date(date):
    if date != "":
        return datetime.strptime(date, '%m-%Y').strftime('%b %Y')
    return date
