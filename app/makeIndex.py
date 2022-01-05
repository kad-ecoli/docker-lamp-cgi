#!/usr/bin/env python3
from string import Template
import os, sys
import textwrap
import re
species_pattern=re.compile("\sOS=([\s\S]+?\sOX=\d+)\s")

rootdir=os.path.dirname(os.path.abspath(__file__))

index_Template=Template('''<html>
<title>Discovery of ERAD substrate by IP-MassSpec</title>
<body>
<p align=justify>
This web portal hosts the Immunoprecipitation-Mass Spectrometry (IP-MS)
datasets used in our discovery of Endoplasmic-Reticulum-associated 
protein Degradation (ERAD) substrate proteins. You may browser individual
datasets or search proteins by gene name or UniProt accession.
</p>

<p>
<form method="post" enctype="multipart/form-data" action="search.cgi">
<table border=0>
<tr border=0>
    <td>Search by protein:</td>
    <td><input type="text" name="NAME" size=30 placeholder="Input UniProt accession or gene name"></td>
    <td><input type="submit" value="submit"></td>
</tr>
</table>
</form>
</p>

<style>
table {
    border-collapse: collapse;
}
</style>

<table style="font-family:Monospace;" border="2px solid black;">
<tr border="1px solid black;">
    <th>#</th>
    <th>Cell line and sample number</th>
    <th>Species and Taxon ID</th>
</tr>
$INDEX_ROWS
</table>

<p>
Copyright 2021-2022 <a href="https://ling-qi.lab.medicine.umich.edu/">Ling Qi lab</a>
</p>

</body>
</html>
''')

individual_Template=Template('''<html>
<title>$SAMPLE</title>
<body>
<p>
<a href=.>[Home]</a> <a href=raw/$SAMPLE.txt download>[Download]</a>
</p>


<style>
table {
    border-collapse: collapse;
    border: 2px solid black;
}
th,td {
    border: 1px solid black;
}
</style>

<style>
.tooltip {
    position: relative;
    display: inline-block;
}
.tooltip .tooltiptext {
    visibility: hidden;
    width: 800px;
    background-color: black;
    color: white;
    text-align: left;
    border-radius: 1px;
    padding: 1px 0;

    position: absolute;
    z-index: 1;
}
.tooltip:hover .tooltiptext {
    visibility: visible;
}
</style>

<table style="font-family:Monospace;">
$INDIVIDUAL_ROWS
</table>

<p>
Copyright 2021-2022 <a href="https://ling-qi.lab.medicine.umich.edu/">Ling Qi lab</a>
</p>

</body>
</html>
''')


wordwidth=20

def getSpecies(sample):
    fp=open("%s/raw/%s.txt"%(rootdir,sample),'r')
    txt=fp.read()
    fp.close()
    match_list=species_pattern.findall(txt)
    match_set=set(match_list)
    species=''
    species_count=0
    for match in set(match_list):
        match_count=match_list.count(match)
        if match_count>=species_count:
            species_count=match_count+0
            species=match.replace(" OX=",' [')+']'
    return species
    

def make_individual_page(sample):
    fp=open("%s/raw/%s.txt"%(rootdir,sample),'r')
    lines=fp.read().splitlines()
    fp.close()
    full_header_list=[item.strip('"') for item in lines[0].split('\t')]
    header_list=["More info"]
    gene_idx=-1
    sele_list=[]
    for i,item in enumerate(full_header_list):
        if item.lower() in ["accession","description","gene symbol"] or \
           item.lower().startswith("# psms (") or \
           item.lower().startswith("abundance:") or \
           (sample.startswith("TMT_") and item.startswith("Abundance") and \
           not item.startswith("Abundances (Grouped)") and \
           not item.startswith("Abundances (Scaled)") and \
           not item.startswith("Abundances Count:") and \
           not item.startswith("Abundances (Normalized)")):
            if item.lower()=="gene symbol":
                gene_idx=i+0
                header_list=header_list[:1]+[item]+header_list[1:]
            else:
                header_list.append(item)
            sele_list.append(i)
    individual_rows="<tr><th>"+"</th><th>".join(header_list)+"</th></tr>\n"
    for line in lines[1:]:
        items=[item.strip('"') for item in line.split('\t')]
        tooltiptext=''
        for i in range(len(items)):
            tooltiptext+="<li><b>%s:</b> %s</li>"%(full_header_list[i],items[i])
        cell_list=["More"]
        for i,item in enumerate(items):
            if not i in sele_list:
                continue
            item=item.strip('"').replace(';','; '
                ).replace("OS=Homo sapiens OX=9606",''
                ).replace("OS=Mus musculus OX=10090",'')
            if full_header_list[i].lower()=="accession":
                cell_list[0]="<a href=all.cgi?ID=%s:%s target=_blank>More</a>"%(
                    sample,item)
                item="<a name=%s>%s</a>"%(item,item)
            if i==gene_idx:
                cell_list=cell_list[:1]+[item.replace('; ',';<br>')]+cell_list[1:]
            else:
                cell_list.append(item)
        individual_rows+="<tr><td>"+"</td><td>".join(cell_list)+"</td></tr>\n"

    fp=open("%s/%s.html"%(rootdir,sample),'w')
    fp.write(individual_Template.substitute({
        "INDIVIDUAL_ROWS":individual_rows,
        "SAMPLE":sample,
    }))
    fp.close()
    return

if __name__=="__main__":
    #### make index.html ####
    fp=open(rootdir+"/list",'r')
    sample_list=fp.read().splitlines()
    fp.close()
    index_rows=''
    for s in range(len(sample_list)): 
        sample=sample_list[s].split('.')[0]
        species=getSpecies(sample)
        index_rows+='''<tr>
    <td>%d</td>
    <td><a href=%s.html>%s</a></td>
    <td>%s</td>
</tr>
'''%(s+1,sample,sample,species)

    fp=open(rootdir+"/index.html",'w')
    fp.write(index_Template.substitute({
        "INDEX_ROWS":index_rows,
    }))
    fp.close()

    #### make individual page ####
    for s in range(len(sample_list)):
        sample=sample_list[s].split('.')[0]
        make_individual_page(sample)
