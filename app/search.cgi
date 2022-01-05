#!/usr/bin/env python3
# For CGI script, we should not use the anaconda python at amino-library,
# which takes a long time to load
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import os
import sys

rootdir=os.path.dirname(os.path.abspath(__file__))

def get_cgi_field():
    '''get cgi input'''
    form = cgi.FieldStorage()
    name=form.getfirst("NAME",'').upper().strip()
    return name

def search_sample(name,sample):
    filename="%s/raw/%s.txt"%(rootdir,sample)
    fp=open(filename,'r')
    lines=[]
    for l,line in enumerate(fp.read().splitlines()):
        if l==0 or name in line.upper():
            lines.append(line)
    fp.close()
    if len(lines)<=1:
        return 0,''
    txt="<p><a name=%s><li>Found %d match in <a href=%s.html>%s</a>. [<a href=#top>back to top</a>]</li></p>\n"%(sample,len(lines)-1,sample,sample)
    header_list=["More info"]
    gene_idx=-1
    sele_list=[]
    full_header_list=[item.strip('"') for item in lines[0].split('\t')]
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
    txt+="<table><tr><th>"+"</th><th>".join(header_list)+"</tr>\n"
    for line in lines[1:]:
        items=[item.strip('"') for item in line.split('\t')]
        accession=items[1]
        tooltiptext=''
        for i in range(len(items)):
            tooltiptext+="<li><b>%s:</b> %s</li>"%(full_header_list[i],items[i])
        cell_list=["<div class=tooltip><a href=all.cgi?ID=%s:%s target=_blank>More</a><span class=tooltiptext>%s</span></div>"%(
            sample,accession,tooltiptext)]
        for i in range(len(items)):
            if not i in sele_list:
                continue
            if i==gene_idx:
                cell_list=cell_list[:1]+[items[i].replace(';',';<br>')]+cell_list[1:]
            else:
                cell_list.append(items[i])
        txt+="<tr><td>"+"</td><td>".join(cell_list)+"</td></tr>\n"
    txt+="</table>\n"
    return len(lines)-1,txt

if __name__=="__main__":
    print("Content-type: text/html\n")
    print("<head><title>Search result</title></head>\n")
    name=get_cgi_field()
    if len(name)==0 and len(sys.argv)==2:
        name=sys.argv[1].upper().strip()

    print("<a href='.'>[back]</a><br>")
    if len(name)==0:
        print("<p>ERROR! Empty keyword</p>")
        exit()
    print('''
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
''')

    fp=open(rootdir+"/list",'r')
    sample_list=[line.split('.')[0] for line in fp.read().splitlines()]
    fp.close()
    totalhitnum=0
    totaltxt=''
    header_list=[]
    for sample in sample_list:
        hitnum,txt=search_sample(name,sample)
        if hitnum:
            totalhitnum+=hitnum
            totaltxt+=txt
            header_list.append("<a href=#%s>%s</a>"%(sample,sample))
    if totalhitnum==0:
        print("<p>No matching hit for keyword &ldquo;%s&rdquo;</p>"%name)
        exit()
    print("<p><a name=top>Found %d matches for keyword &ldquo;%s&rdquo; in: %s.</p>"%(totalhitnum,name,', '.join(header_list)))
    print(totaltxt)
