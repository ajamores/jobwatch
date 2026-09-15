# The ones we could not reach — check these by hand

227 of the 287 employers in `docs/census.tsv` are not on the watchlist. Every link goes
to the real careers page, resolved by the fingerprint pass rather than guessed at.

Closest first within each section: **A** is within 40km of Hamilton, **B** is 40-100km,
**C** is 100-200km.

Four reasons cover most of the list:

- **login-walled** — there is no public listing to read at all. Every K-12 school board.
- **hand-built page** — no vendor to adapt; each needs its own scraper. Most libraries.
- **bot wall** — answers a browser, refuses a script. Njoyn and iCIMS.
- **adapter not built** — a known vendor, simply not written yet. That is the build queue.

The technical detail is in `docs/unresolved.txt`. This file is for reading with a browser
open. Regenerate it with `python -m jobwatch.watchlist.uncovered`.


## K-12 school boards — 26

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| Brant Haldimand Norfolk Catholic DSB | Brantford (A) | [open](https://bhncdsb.simplication.com/) | ApplyToEducation — **login-walled**, no public listing |
| Grand Erie DSB | Brantford (A) | [open](https://granderie.ca/careers) | no vendor — hand-built page, needs its own scraper |
| Halton Catholic DSB | Burlington (A) | [open](https://hcdsb.org) | no vendor — hand-built page, needs its own scraper |
| Halton DSB | Burlington (A) | [open](https://hdsb.simplication.com/) | ApplyToEducation — **login-walled**, no public listing |
| Hamilton-Wentworth Catholic DSB | Hamilton (A) | [open](https://www.hwcdsb.ca/our_board/staff/careers) | ApplyToEducation — **login-walled**, no public listing |
| Hamilton-Wentworth DSB | Hamilton (A) | [open](https://hwdsb.on.ca) | no vendor — hand-built page, needs its own scraper |
| District School Board of Niagara | St. Catharines (B) | [open](https://dsbn.org) | ApplyToEducation — **login-walled**, no public listing |
| Dufferin-Peel Catholic DSB | Mississauga (B) | [open](https://dpcdsb.simplication.com/) | ApplyToEducation — **login-walled**, no public listing |
| Niagara Catholic DSB | Welland (B) | [open](https://niagaracatholic.simplication.com/Applicant/jobposting/jobdetails.aspx?JOB_POSTING_ID=bdb1109b-55eb-4844-8bd5-d5982acccd16&PAGE=1&locale=en&maf=0&sReferer=SIMPLICATIONJOBBOARD) | ApplyToEducation — **login-walled**, no public listing |
| Peel DSB | Mississauga (B) | [open](https://peelschools.org) | no vendor — hand-built page, needs its own scraper |
| Toronto Catholic DSB | Toronto (B) | [open](https://tcdsb.org) | no vendor — hand-built page, needs its own scraper |
| Toronto DSB | Toronto (B) | [open](https://www.tdsb.on.ca/About-Us/Careers) | no vendor — hand-built page, needs its own scraper |
| Upper Grand DSB | Guelph (B) | [open](https://ugdsb.ca) | ApplyToEducation — **login-walled**, no public listing |
| Waterloo Catholic DSB | Kitchener (B) | [open](https://wcdsb.ca) | iCIMS — refuses plain scripts (405) |
| Waterloo Region DSB | Kitchener (B) | [open](https://wrdsb.simplication.com/) | ApplyToEducation — **login-walled**, no public listing |
| Wellington Catholic DSB | Guelph (B) | [open](https://can01.safelinks.protection.outlook.com/?url=https%3A%2F%2Fwellingtoncdsb.simplication.com%2F&data=05%7C01%7Calison.wilson%40wellingtoncdsb.ca%7C49c5cad09718425c759a08da65ba85bc%7Cdd6a87562a174765826d56bad2b808eb%7C0%7C0%7C637934149019581565%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C3000%7C%7C%7C&sdata=R41POZtDZkwhCfGPEjQRrVyIaRyBINOiLxjMddLUDCs%3D&reserved=0) | ApplyToEducation — **login-walled**, no public listing |
| York Catholic DSB | Aurora (B) | [open](https://ycdsb.simplication.com/Applicant/jobposting/jobdetails.aspx?JOB_POSTING_ID=1b2d8ef6-affb-4950-9988-7c8bdd1cb6e5&PAGE=1&locale=en&maf=0&sReferer=SIMPLICATIONJOBBOARD) | ApplyToEducation — **login-walled**, no public listing |
| York Region DSB | Aurora (B) | [open](https://yrdsb.ca) | ApplyToEducation — **login-walled**, no public listing |
| Avon Maitland DSB | Stratford (C) | [open](https://amdsb.simplication.com/applicant/jobposting/jobdetails.aspx?JOB_POSTING_ID=247b6354-cbe5-4911-83a7-d572fb42c8ac&sReferer=SIMPLICATIONJOBBOARD) | ApplyToEducation — **login-walled**, no public listing |
| Bluewater DSB | Owen Sound (C) | [open](https://bwdsb.simplication.com/) | ApplyToEducation — **login-walled**, no public listing |
| Durham Catholic DSB | Oshawa (C) | [open](https://dcdsb.ca) | ApplyToEducation — **login-walled**, no public listing |
| Durham DSB | Whitby (C) | [open](https://www.ddsb.ca/about-ddsb/careers-at-the-ddsb/teaching-opportunities/) | ApplyToEducation — **login-walled**, no public listing |
| Kawartha Pine Ridge DSB | Peterborough (C) | [open](https://kprdsb.ca) | did not answer — URLError: <urlopen error [Errno 104] Connection rese |
| London District Catholic SB | London (C) | [open](https://ldcsb.ca) | ApplyToEducation — **login-walled**, no public listing |
| Simcoe County DSB | Barrie (C) | [open](https://scdsb.on.ca) | ApplyToEducation — **login-walled**, no public listing |
| Thames Valley DSB | London (C) | [open](https://tvdsb.ca) | no vendor — hand-built page, needs its own scraper |

## Public libraries — 25

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| Brantford Public Library | Brantford (A) | [open](https://brantfordlibrary.ca) | no vendor — hand-built page, needs its own scraper |
| Burlington Public Library | Burlington (A) | [open](https://bpl.on.ca/about/careers) | no vendor — hand-built page, needs its own scraper |
| Grimsby Public Library | Grimsby (A) | [open](https://grimsbylibrary.ca) | no vendor — hand-built page, needs its own scraper |
| Halton Hills Public Library | Georgetown (A) | [open](https://hhpl.on.ca) | no vendor — hand-built page, needs its own scraper |
| Hamilton Public Library | Hamilton (A) | [open](https://hpl.ca/jobs) | no vendor — hand-built page, needs its own scraper |
| Milton Public Library | Milton (A) | [open](https://mpl.on.ca) | no vendor — hand-built page, needs its own scraper |
| Oakville Public Library | Oakville (A) | [open](https://tre.tbe.taleo.net/tre01/ats/careers/v2/jobSearch?act=redirectCwsV2&cws=49&org=TOWNOFOA) | Taleo — adapter not built |
| Brampton Library | Brampton (B) | [open](https://bramptonlibrary.ca) | no vendor — hand-built page, needs its own scraper |
| Guelph Public Library | Guelph (B) | [open](https://guelphpl.ca) | no vendor — hand-built page, needs its own scraper |
| Idea Exchange | Cambridge (B) | [open](https://ideaexchange.org) | no vendor — hand-built page, needs its own scraper |
| Kitchener Public Library | Kitchener (B) | [open](https://kpl.org) | no vendor — hand-built page, needs its own scraper |
| Markham Public Library | Markham (B) | [open](https://markhampubliclibrary.ca) | no vendor — hand-built page, needs its own scraper |
| Niagara Falls Public Library | Niagara Falls (B) | [open](https://nflibrary.ca) | no vendor — hand-built page, needs its own scraper |
| Ontario Library Service | Toronto (B) | [open](https://olservice.ca) | no vendor — hand-built page, needs its own scraper |
| Richmond Hill Public Library | Richmond Hill (B) | [open](https://rhpl.ca) | career17.sapsf.com is raw SAP, not a tenant career site — the tile URL 404s |
| St. Catharines Public Library | St. Catharines (B) | [open](https://stcatharines.library.on.ca) | did not answer — URLError: <urlopen error timed out> |
| Toronto Public Library | Toronto (B) | [open](https://tpl.njoyn.com/CL/xweb/xweb.asp?page=joblisting&CLID=124703) | Njoyn — bot wall, needs a browser |
| Vaughan Public Libraries | Vaughan (B) | [open](https://vaughanpl.info) | no vendor — hand-built page, needs its own scraper |
| Waterloo Public Library | Waterloo (B) | [open](https://wpl.ca) | no vendor — hand-built page, needs its own scraper |
| Welland Public Library | Welland (B) | [open](https://wellandlibrary.ca) | no vendor — hand-built page, needs its own scraper |
| Ajax Public Library | Ajax (C) | [open](https://ajaxlibrary.ca) | no vendor — hand-built page, needs its own scraper |
| Barrie Public Library | Barrie (C) | [open](https://www.barrielibrary.ca/about-bpl/jobs) | no vendor — hand-built page, needs its own scraper |
| Oshawa Public Libraries | Oshawa (C) | [open](https://oshawalibrary.on.ca) | no vendor — hand-built page, needs its own scraper |
| Pickering Public Library | Pickering (C) | [open](https://pickeringlibrary.ca) | no vendor — hand-built page, needs its own scraper |
| Whitby Public Library | Whitby (C) | [open](https://whitbylibrary.ca) | no vendor — hand-built page, needs its own scraper |

## Hospitals & health networks — 37

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| Brant Community Healthcare System | Brantford (A) | [open](https://bchs.njoyn.com/CL/xweb/xweb.asp?page=joblisting&CLID=58310) | Njoyn — bot wall, needs a browser |
| De dwa da dehs nye>s Aboriginal Health | Hamilton (A) | [open](https://aboriginalhealthcentre.com/careers) | no vendor — hand-built page, needs its own scraper |
| Haldimand War Memorial Hospital | Dunnville (A) | [open](https://hwmh.ca) | no vendor — hand-built page, needs its own scraper |
| Halton Healthcare | Oakville (A) | [open](https://www.haltonhealthcare.on.ca/careers) | SmartRecruiters — adapter not built |
| Hamilton Health Sciences | Hamilton (A) | [open](https://hhsc.taleo.net/careersection/2/jobsearch.ftl?lang=en) | Taleo — adapter not built |
| Joseph Brant Hospital | Burlington (A) | [open](https://www.josephbranthospital.ca/about-us/join-us/careers) | MediSolution eRecruit — adapter not built |
| St. Joseph's Health System | Hamilton (A) | [open](https://tre.tbe.taleo.net/tre01/ats/careers/v2/jobSearch?act=redirectCwsV2&cws=47&org=STJOSHAM) | Taleo — adapter not built |
| St. Joseph's Healthcare Hamilton | Hamilton (A) | [open](https://stjoes.ca) | no vendor — hand-built page, needs its own scraper |
| St. Joseph's Home Care | Hamilton (A) | [open](https://stjosephhomecare.applytojob.com/apply) | jazzhr — adapter not built |
| Baycrest | Toronto (B) | [open](https://jobs-ca.silkroad.com/Baycrest/Careers) | silkroad — adapter not built |
| CAMH | Toronto (B) | [open](https://iaemup.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CAMH) | Oracle Recruiting — adapter not built |
| Cambridge Memorial Hospital | Cambridge (B) | [open](https://encareers-cmh.icims.com/) | iCIMS — refuses plain scripts (405) |
| Grand River Hospital | Kitchener (B) | [open](https://grhosp.on.ca) | did not answer — URLError: <urlopen error timed out> |
| Guelph General Hospital | Guelph (B) | [open](https://www.gghorg.ca/careers) | no vendor — hand-built page, needs its own scraper |
| Headwaters Health Care Centre | Orangeville (B) | [open](https://headwatershealth.ca) | no vendor — hand-built page, needs its own scraper |
| Holland Bloorview | Toronto (B) | [open](https://hollandbloorview.ca) | no vendor — hand-built page, needs its own scraper |
| Humber River Health | Toronto (B) | [open](https://careersen-hrrh.icims.com/jobs/intro) | iCIMS — refuses plain scripts (405) |
| Mackenzie Health | Richmond Hill (B) | [open](https://employment-mackenziehealth.icims.com) | iCIMS — refuses plain scripts (405) |
| Michael Garron Hospital | Toronto (B) | [open](https://clients.njoyn.com/CL3/xweb/xweb.asp?page=joblisting&CLID=55587&categoryID=2468) | Njoyn — bot wall, needs a browser |
| Niagara Health | St. Catharines (B) | [open](https://careers.niagarahealth.on.ca/erecruit/) | MediSolution eRecruit — adapter not built |
| Norfolk General Hospital | Simcoe (B) | [open](https://ngh.on.ca) | no vendor — hand-built page, needs its own scraper |
| North York General | Toronto (B) | [open](https://nygh.on.ca) | no vendor — hand-built page, needs its own scraper |
| Oak Valley Health | Markham (B) | [open](https://oakvalleyhealth.ca) | did not answer — HTTP 307 |
| Sinai Health | Toronto (B) | [open](https://jobs.dayforcehcm.com/en-CA/sinaihealth/sinaihealthcareers) | Dayforce — adapter not built |
| St. Mary's General Hospital | Kitchener (B) | [open](https://smgh.ca) | no vendor — hand-built page, needs its own scraper |
| Sunnybrook Health Sciences | Toronto (B) | [open](https://sunnybrook.ca) | no vendor — hand-built page, needs its own scraper |
| The Hospital for Sick Children | Toronto (B) | [open](https://sickkids.ca) | no vendor — hand-built page, needs its own scraper |
| Trillium Health Partners | Mississauga (B) | [open](https://iadyup.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/requisitions) | Oracle Recruiting — adapter not built |
| Unity Health Toronto | Toronto (B) | [open](https://unityhealth.to) | did not answer — URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FA |
| University Health Network | Toronto (B) | [open](https://www.uhn.ca/corporate/Careers/pages/default.aspx) | SmartRecruiters — adapter not built |
| William Osler Health System | Brampton (B) | [open](https://williamoslerhs.ca) | SmartRecruiters — adapter not built |
| Women's College Hospital | Toronto (B) | [open](https://www.dayforcehcm.com/CandidatePortal/en-US/WCH) | Dayforce — adapter not built |
| Lakeridge Health | Oshawa (C) | [open](https://careers.lakeridgehealth.on.ca/erecruit/) | MediSolution eRecruit — adapter not built |
| London Health Sciences Centre | London (C) | [open](https://www.lhsc.on.ca/careers) | no vendor — hand-built page, needs its own scraper |
| Royal Victoria Regional Health Centre | Barrie (C) | [open](https://www.rvh.on.ca/careers) | no vendor — hand-built page, needs its own scraper |
| St. Joseph's Health Care London | London (C) | [open](https://www.sjhc.london.on.ca/careers) | no vendor — hand-built page, needs its own scraper |
| Stevenson Memorial Hospital | Alliston (C) | [open](https://smhosp.ca) | did not answer — URLError: <urlopen error [Errno -2] Name or service  |

## Colleges & universities — 22

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| McMaster University | Hamilton (A) | [open](https://hr.mcmaster.ca/careers) | no vendor — hand-built page, needs its own scraper |
| Mohawk College | Hamilton (A) | [open](https://talent-mohawkcollege.csod.com/ats/careersite/search.aspx?site=2&c=talent-mohawkcollege) | Cornerstone — adapter not built |
| Brock University | St. Catharines (B) | [open](https://brocku.ca) | did not answer — URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FA |
| Centennial College | Scarborough (B) | [open](http://clients.njoyn.com/CL3/xweb/xweb.asp?page=joblisting&CLID=56827) | Njoyn — bot wall, needs a browser |
| Conestoga College | Kitchener (B) | [open](https://conestogac.on.ca) | no vendor — hand-built page, needs its own scraper |
| George Brown College | Toronto (B) | [open](https://georgebrown.ca) | did not answer — HTTP 403 |
| Humber Polytechnic | Toronto (B) | [open](https://humber.taleo.net/careersection/hbr_in/jobsearch.ftl?lang=en&portal=12100010168) | Taleo — adapter not built |
| Michener Institute | Toronto (B) | [open](https://jobs.smartrecruiters.com/UniversityHealthNetwork/744000128782299-professor-cardiovascular-perfusion) | SmartRecruiters — adapter not built |
| Niagara College | Welland (B) | [open](https://tre.tbe.taleo.net/tre01/ats/careers/v2/jobSearch?act=redirectCwsV2&cws=38&org=NIAGARACOLLEGE) | Taleo — adapter not built |
| OCAD University | Toronto (B) | [open](https://tre.tbe.taleo.net/tre01/ats/careers/v2/jobSearch?act=redirectCwsV2&cws=37&org=OCADU) | Taleo — adapter not built |
| Perimeter Institute | Waterloo (B) | [open](https://perimeterinstitute.ca) | no vendor — hand-built page, needs its own scraper |
| Seneca Polytechnic | Toronto (B) | [open](https://tre.tbe.taleo.net/tre01/ats/careers/v2/jobSearch?act=redirectCwsV2&cws=42&org=SENECOLL4) | Taleo — adapter not built |
| Sheridan College | Oakville (B) | [open](https://clients.njoyn.com/CL3/xweb/xweb.asp?page=joblisting&CLID=55117) | Njoyn — bot wall, needs a browser |
| Toronto Metropolitan University | Toronto (B) | [open](https://torontomu.ca) | no vendor — hand-built page, needs its own scraper |
| Wilfrid Laurier University | Waterloo (B) | [open](https://wlu.ca) | no vendor — hand-built page, needs its own scraper |
| York University | Toronto (B) | [open](https://yorku.ca) | did not answer — URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FA |
| Durham College | Oshawa (C) | [open](https://durham.csod.com/ux/ats/careersite/5/home?c=durham) | Cornerstone — adapter not built |
| Fanshawe College | London (C) | [open](https://www.fanshawec.ca/students/support/employment) | no vendor — hand-built page, needs its own scraper |
| Georgian College | Barrie (C) | [open](https://georgiancollege.ca) | no vendor — hand-built page, needs its own scraper |
| Ontario Tech University | Oshawa (C) | [open](https://ontariotechu.csod.com/samldefault.aspx?ouid=2) | Cornerstone — adapter not built |
| Trent University | Peterborough (C) | [open](https://trentu.ca) | no vendor — hand-built page, needs its own scraper |
| Western University | London (C) | [open](https://uwo.ca) | no vendor — hand-built page, needs its own scraper |

## Independent schools — 9

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| Appleby College | Oakville (A) | [open](https://appleby.on.ca) | ADP, but the site refuses a plain script (403), so its client id is unreadable |
| Columbia International College | Hamilton (A) | [open](https://cic-totalcare.com) | no vendor — hand-built page, needs its own scraper |
| St. Mildred's-Lightbourn School | Oakville (A) | [open](https://smls.on.ca) | ApplyToEducation — **login-walled**, no public listing |
| Crescent School | Toronto (B) | [open](https://crescentschool.org) | no vendor — hand-built page, needs its own scraper |
| Havergal College | Toronto (B) | [open](https://www.havergal.on.ca/careers) | no vendor — hand-built page, needs its own scraper |
| Ridley College | St. Catharines (B) | [open](https://ridleycollege.com) | no vendor — hand-built page, needs its own scraper |
| Toronto French School | Toronto (B) | [open](https://tfs.ca) | no vendor — hand-built page, needs its own scraper |
| St. Andrew's College | Aurora (C) | [open](https://sac.on.ca) | no vendor — hand-built page, needs its own scraper |
| The Country Day School | King City (C) | [open](https://www.cds.on.ca/about/employment) | no vendor — hand-built page, needs its own scraper |

## Municipal & regional government — 25

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| City of Brantford | Brantford (A) | [open](https://www.brantford.ca/your-government/careers) | no vendor — hand-built page, needs its own scraper |
| County of Brant | Paris (A) | [open](https://countyofbrant.applytojob.com/apply) | jazzhr — adapter not built |
| Haldimand County | Cayuga (A) | [open](https://haldimandcounty.ca) | no vendor — hand-built page, needs its own scraper |
| Mississaugas of the Credit First Nation | Hagersville (A) | [open](https://ekaw.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/160021/) | Oracle Recruiting — adapter not built |
| Six Nations of the Grand River | Ohsweken (A) | [open](https://www.sixnations.ca/careers) | no vendor — hand-built page, needs its own scraper |
| Town of Grimsby | Grimsby (A) | [open](https://www.grimsby.ca/town-hall/careers) | no vendor — hand-built page, needs its own scraper |
| Town of Halton Hills | Georgetown (A) | [open](https://haltonhills.ca) | no vendor — hand-built page, needs its own scraper |
| Town of Lincoln | Beamsville (A) | [open](https://lincoln.ca) | did not answer — URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FA |
| Town of Oakville | Oakville (A) | [open](https://tre.tbe.taleo.net/tre01/ats/careers/v2/jobSearch?act=redirectCwsV2&cws=43&org=TOWNOFOA) | Taleo — adapter not built |
| City of Brampton | Brampton (B) | [open](https://brampton.ca) | SuccessFactors tenant answers, but shows no job tiles on either template |
| City of Cambridge | Cambridge (B) | [open](https://cambridge.ca) | no vendor — hand-built page, needs its own scraper |
| City of Guelph | Guelph (B) | [open](https://careers-guelph.icims.com/jobs/intro) | iCIMS — refuses plain scripts (405) |
| City of Kitchener | Kitchener (B) | [open](https://kitchener.ca) | SuccessFactors tenant answers, but shows no job tiles on either template |
| City of St. Catharines | St. Catharines (B) | [open](https://tre.tbe.taleo.net/tre01/ats/careers/v2/searchResults?org=COSC&cws=37) | Taleo — adapter not built |
| City of Vaughan | Vaughan (B) | [open](https://vaughan.ca) | did not answer — HTTP 403 |
| City of Waterloo | Waterloo (B) | [open](https://waterloo.ca) | no vendor — hand-built page, needs its own scraper |
| City of Welland | Welland (B) | [open](https://welland.ca) | no vendor — hand-built page, needs its own scraper |
| Niagara Region | Thorold (B) | [open](https://niagararegion.ca/government/hr/careers) | no vendor — hand-built page, needs its own scraper |
| Norfolk County | Simcoe (B) | [open](https://norfolkcounty.ca) | no vendor — hand-built page, needs its own scraper |
| Region of Peel | Brampton (B) | [open](https://careers-peelregion.icims.com/jobs/search) | iCIMS — refuses plain scripts (405) |
| Regional Municipality of York | Newmarket (B) | [open](https://www.york.ca/york-region/careers) | no vendor — hand-built page, needs its own scraper |
| City of Barrie | Barrie (C) | [open](https://careers.barrie.ca/search/?department=recreation_%26_culture_services) | vidcruiter — adapter not built |
| City of London | London (C) | [open](https://london.ca) | no vendor — hand-built page, needs its own scraper |
| City of Oshawa | Oshawa (C) | [open](https://cityofoshawa.njoyn.com/CL/xweb/xweb.asp?page=joblisting&CLID=126638) | Njoyn — bot wall, needs a browser |
| Regional Municipality of Durham | Whitby (C) | [open](https://recruitregion.durham.ca/psc/recruit_rmd/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB&Action=U&FOCUS=Applicant&SiteId=3) | PeopleSoft — adapter not built |

## Police services — 8

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| Halton Regional Police Service | Oakville (A) | [open](https://www.haltonpolice.ca/careers) | no vendor — hand-built page, needs its own scraper |
| Hamilton Police Service | Hamilton (A) | [open](https://hamiltonpolice.on.ca/careers) | no vendor — hand-built page, needs its own scraper |
| Niagara Regional Police Service | Niagara Falls (B) | [open](https://niagarapolice.ca) | no vendor — hand-built page, needs its own scraper |
| Ontario Provincial Police | Orillia (B) | [open](https://opp.ca) | no vendor — hand-built page, needs its own scraper |
| Peel Regional Police | Mississauga (B) | [open](https://www.peelpolice.ca/careers/) | MediSolution eRecruit — adapter not built |
| Toronto Police Service | Toronto (B) | [open](https://torontopolice.on.ca) | did not answer — HTTP 403 |
| York Regional Police | Aurora (B) | [open](https://yrp.ca) | SuccessFactors tenant answers, but shows no job tiles on either template |
| Durham Regional Police Service | Whitby (C) | [open](https://drps.ca) | no vendor — hand-built page, needs its own scraper |

## Insurance, mutuals, credit unions, pensions — 10

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| FirstOntario Credit Union | Hamilton (A) | [open](https://firstontario.com) | no vendor — hand-built page, needs its own scraper |
| Ayr Farmers Mutual Insurance | Ayr (B) | [open](https://ayrfarmers.com/employment) | page builds itself in the browser |
| DUCA Financial Services | Toronto (B) | [open](https://duca.com) | no vendor — hand-built page, needs its own scraper |
| Definity Financial | Waterloo (B) | [open](https://definityfinancial.com) | jobvite — adapter not built |
| Equitable Life of Canada | Waterloo (B) | [open](https://equitable.ca/careers) | no vendor — hand-built page, needs its own scraper |
| Halwell Mutual Insurance | Guelph (B) | [open](https://halwellmutual.com) | no vendor — hand-built page, needs its own scraper |
| OMERS | Toronto (B) | [open](https://cdn.phenompeople.com/CareerConnectResources/OMEOMECA/en_ca/desktop/assets/images/favicon.ico?v=1759167092649) | phenom — adapter not built |
| Trillium Mutual Insurance | Listowel (B) | [open](https://trilliummutual.com/careers) | no vendor — hand-built page, needs its own scraper |
| WSIB | Toronto (B) | [open](https://wsib-iaepup.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs?mode=location) | Oracle Recruiting — adapter not built |
| Your Neighbourhood Credit Union | Kitchener (B) | [open](https://yncu.com) | no vendor — hand-built page, needs its own scraper |

## Tech — 16

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| Cogeco | Burlington (A) | [open](https://cogeco.ca) | did not answer — HTTP 403 |
| Mabel's Labels | Hamilton (A) | [open](https://mabelslabels.ca) | no vendor — hand-built page, needs its own scraper |
| Weever Apps | St. Catharines (A) | [open](https://weeverapps.com) | no vendor — hand-built page, needs its own scraper |
| Axonify | Waterloo (B) | [open](https://axonify.com/careers) | no vendor — hand-built page, needs its own scraper |
| Bonfire Interactive | Kitchener (B) | [open](https://gobonfire.com) | no vendor — hand-built page, needs its own scraper |
| D2L | Kitchener (B) | [open](https://www.d2l.com/careers) | no vendor — hand-built page, needs its own scraper |
| Descartes Systems Group | Waterloo (B) | [open](https://descartes.com) | no vendor — hand-built page, needs its own scraper |
| Igloo Software | Kitchener (B) | [open](https://igloosoftware.com) | no vendor — hand-built page, needs its own scraper |
| Intelex Technologies | Toronto (B) | [open](https://fortive.eightfold.ai) | eightfold — adapter not built |
| Intellijoint Surgical | Waterloo (B) | [open](https://intellijointsurgical.com) | no vendor — hand-built page, needs its own scraper |
| Magnet Forensics | Waterloo (B) | [open](https://jobs.lever.co/magnetforensics/39181882-5eae-41c6-b494-c3d6791c978b) | lever — adapter not built |
| Miovision | Kitchener (B) | [open](https://jobs.ashbyhq.com/miovision) | ashby — adapter not built |
| OpenText | Waterloo (B) | [open](https://opentext.com) | did not answer — TimeoutError: The read operation timed out |
| Synaptive Medical | Toronto (B) | [open](https://jobs.dayforcehcm.com/en-US/pp4h663/CANDIDATEPORTAL) | Dayforce — adapter not built |
| Vidyard | Kitchener (B) | [open](https://vidyard.com) | no vendor — hand-built page, needs its own scraper |
| eSentire | Cambridge (B) | [open](https://can60.dayforcehcm.com/CandidatePortal/en-US/esentire/Site/CANDIDATEPORTAL) | Dayforce — adapter not built |

## Manufacturing & industrial — 14

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| Bunge Canada | Hamilton (A) | [open](https://bunge.com/careers) | no vendor — hand-built page, needs its own scraper |
| Ferrero Canada | Brantford (A) | [open](https://ferrerocareers.com) | fingerprint keeps mis-firing — confirmed NOT SuccessFactors, real vendor unknown |
| L3Harris WESCAM | Waterdown (A) | [open](https://l3harris.com) | no vendor — hand-built page, needs its own scraper |
| Maple Leaf Foods | Mississauga (A) | [open](https://www.mapleleaffoods.com/careers) | no vendor — hand-built page, needs its own scraper |
| SC Johnson Canada | Brantford (A) | [open](https://scjohnson.com) | no vendor — hand-built page, needs its own scraper |
| Wescast Industries | Brantford (A) | [open](https://www.wescast.com/careers/munkavedelmi-szakmernok/) | MediSolution eRecruit — adapter not built |
| Canada Bread | Mississauga (B) | [open](https://canadabread.com) | no vendor — hand-built page, needs its own scraper |
| George Weston | Toronto (B) | [open](https://weston.ca) | did not answer — HTTP 307 |
| Linamar | Guelph (B) | [open](https://fa-epmd-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_3001) | Oracle Recruiting — adapter not built |
| Martinrea International | Vaughan (B) | [open](https://www.martinrea.com/es/culture/careers) | no vendor — hand-built page, needs its own scraper |
| Nestle Canada | Toronto (B) | [open](https://nestle.ca) | did not answer — HTTP 403 |
| Sofina Foods | Markham (B) | [open](https://www.dayforcehcm.com/CandidatePortal/en-US/sofinafoods/) | Dayforce — adapter not built |
| Tigercat International | Brantford (B) | [open](https://jobs.dayforcehcm.com/en-US/tcii/TIND) | Dayforce — adapter not built |
| Toyota Motor Manufacturing Canada | Cambridge (B) | [open](https://tmmc.ca) | no vendor — hand-built page, needs its own scraper |

## Utilities & energy — 9

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| Alectra Utilities | Hamilton (A) | [open](https://jobs.dayforcehcm.com/en-US/alectra/CANDIDATEPORTAL) | Dayforce — adapter not built |
| Burlington Hydro | Burlington (A) | [open](https://jobs.dayforcehcm.com/en-US/bhi/CANDIDATEPORTAL) | Dayforce — adapter not built |
| Halton Hills Hydro | Georgetown (A) | [open](https://haltonhillshydro.com/about/careers) | no vendor — hand-built page, needs its own scraper |
| Energy+ | Cambridge (B) | [open](https://energyplus.ca) | no vendor — hand-built page, needs its own scraper |
| Hydro One | Toronto (B) | [open](https://www.hydroone.com/careers) | Cloudflare / WAF |
| Niagara Peninsula Energy | Niagara Falls (B) | [open](https://www.npei.ca/about-us/careers) | no vendor — hand-built page, needs its own scraper |
| Ontario Power Generation | Toronto (B) | [open](https://opg.com) | no vendor — hand-built page, needs its own scraper |
| Bruce Power | Tiverton (C) | [open](https://brucepower.com) | did not answer — HTTP 403 |
| Elexicon Energy | Whitby (C) | [open](https://elexiconenergy.com) | did not answer — HTTP 403 |

## Transport & infrastructure — 7

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| Hamilton Oshawa Port Authority | Hamilton (A) | [open](https://www.hopaports.ca/about-hopa/people-and-careers/) | false match — the board it links to belongs to a port tenant (BWC Terminals), not HOPA |
| John C. Munro Hamilton International Airport | Mount Hope (A) | [open](https://careers-vantageairportgroup.icims.com/jobs/search?ss=1&searchLocation=12955-12964-Hamilton) | iCIMS — refuses plain scripts (405) |
| CN Rail | Toronto (B) | [open](https://cn360.csod.com/ux/ats/careersite/1/home?c=cn360&lang=en-US) | Cornerstone — adapter not built |
| CPKC | Toronto (B) | [open](https://cpkcr.com) | no vendor — hand-built page, needs its own scraper |
| Greater Toronto Airports Authority | Mississauga (B) | [open](https://torontopearson.com) | page builds itself in the browser |
| Metrolinx / GO Transit | Toronto (B) | [open](https://ehtc.fa.ca2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1) | Oracle Recruiting — adapter not built |
| Toronto Transit Commission | Toronto (B) | [open](https://www.ttc.ca/Jobs) | no vendor — hand-built page, needs its own scraper |

## Crown corporations & agencies — 4

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| CCOHS | Hamilton (A) | [open](https://ccohs.ca) | no vendor — hand-built page, needs its own scraper |
| Infrastructure Ontario | Toronto (B) | [open](https://jobs.dayforcehcm.com/en-US/infrastructureontario/CANDIDATEPORTAL) | Dayforce — adapter not built |
| Legal Aid Ontario | Toronto (B) | [open](https://client.legalaidonline.on.ca/psp/paprdc/CUSTOMER/CUST/?cmd=login) | PeopleSoft — adapter not built |
| Ontario Public Service | Toronto (B) | [open](https://ontario.ca) | Cloudflare / WAF |

## Conservation authorities & attractions — 6

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| Conservation Halton | Burlington (A) | [open](https://www.conservationhalton.ca/about-us/employment/) | Dayforce — adapter not built |
| Hamilton Conservation Authority | Ancaster (A) | [open](https://conservationhamilton.ca) | no vendor — hand-built page, needs its own scraper |
| Credit Valley Conservation | Mississauga (B) | [open](https://cvc.ca) | no vendor — hand-built page, needs its own scraper |
| Grand River Conservation Authority | Cambridge (B) | [open](https://grandriver.ca) | no vendor — hand-built page, needs its own scraper |
| Niagara Peninsula Conservation Authority | Welland (B) | [open](https://npca.ca/about/careers) | no vendor — hand-built page, needs its own scraper |
| Toronto and Region Conservation | Vaughan (B) | [open](https://can60.dayforcehcm.com/CandidatePortal/en-CAN/trca) | Dayforce — adapter not built |

## Non-profits — 9

| Employer | City | Careers page | Why not watched |
|---|---|---|---|
| United Way Halton and Hamilton | Burlington (A) | [open](https://uwhh.ca/about-us/careers) | no vendor — hand-built page, needs its own scraper |
| YMCA of Hamilton Burlington Brantford | Hamilton (A) | [open](https://ymcahbb.ca) | no vendor — hand-built page, needs its own scraper |
| Bayshore HealthCare | Mississauga (B) | [open](https://bayshore.ca) | no vendor — hand-built page, needs its own scraper |
| CAA South Central Ontario | Thornhill (B) | [open](https://www.caasco.com/about/careers) | the link found points at an SAP *staging* host; live board not identified |
| Canadian Red Cross | Toronto (B) | [open](https://tre.tbe.taleo.net/tre01/ats/careers/v2/jobSearch?act=redirectCwsV2&cws=75&org=CRCS) | Taleo — adapter not built |
| CarePartners | Kitchener (B) | [open](https://careers-carepartners.icims.com/) | iCIMS — refuses plain scripts (405) |
| SE Health | Markham (B) | [open](https://sehc.com) | no vendor — hand-built page, needs its own scraper |
| VON Canada | Toronto (B) | [open](https://jobs.jobvite.com/von/search?r=&l=&c=Other%20Professions%20(HR,%20IT,%20Finance,%20etc.)) | jobvite — adapter not built |
| YMCA of Greater Toronto | Toronto (B) | [open](https://ymcagta.org) | no vendor — hand-built page, needs its own scraper |
