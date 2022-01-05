#!/usr/bin/env python3
# For CGI script, we should not use the anaconda python at amino-library,
# which takes a long time to load
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import os

rootdir=os.path.dirname(os.path.abspath(__file__))

def get_cgi_field():
    '''get cgi input'''
    form = cgi.FieldStorage()
    ID=form.getfirst("ID",'').strip()
    return ID

def show_entry(sample,accession):
    filename="%s/raw/%s.txt"%(rootdir,sample)
    fp=open(filename,'r')
    lines=[]
    for l,line in enumerate(fp.read().splitlines()):
        if l==0 or '\t'+accession+'\t' in line:
            lines.append(line)
    fp.close()
    header_list=[]
    accession_col=1
    for i,item in enumerate(lines[0].split('\t')):
        item=item.strip('"')
        if item.lower()=="accession":
           accession_col=i+0
        header_list.append(item)
    txt="<table><tr><th>"+"</th><th>".join(header_list)+"</tr>\n"
    for line in lines[1:]:
        items=line.split('\t')
        if items[accession_col]!=accession:
            continue
        cell_list=[item.strip('"') for item in items]
        txt+="<tr><td>"+"</td><td>".join(items)+"</td></tr>\n"
    txt+="</table>\n"
    return txt

if __name__=="__main__":
    print("Content-type: text/html\n")
    ID=get_cgi_field()
    print("<head><title>%s</title></head>\n"%ID)
    if ID.count(':')!=1:
        print("<p>ERROR! Incorrect ID format:<br>%s<br></p>"%ID)
        exit()
    sample,accession=ID.split(':')
    print('''
<style>
table {
    border-collapse: collapse;
    border: 2px solid black;
}
th,td {
    border: 1px solid black;
}
</style>''')

    fp=open(rootdir+"/list",'r')
    sample_list=[line.split('.')[0] for line in fp.read().splitlines()]
    fp.close()
    if not sample in sample_list:
        print("<p>ERROR! No such sample %s</p>"%(sample))
    print(show_entry(sample,accession))
    print("<p></p><a href=%s.html#%s>[View entry in the full dataset]</a>"%(sample,accession))
