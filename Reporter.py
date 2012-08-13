#!/usr/bin/python3
# Copyright 2011 Francisco Pina Martins <f.pinamartins@gmail.com>
# This file is part of 4Pipe4.
# 4Pipe4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# 4Pipe4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with 4Pipe4.  If not, see <http://www.gnu.org/licenses/>.

import re
import os

def FASTAtoDict(fasta):
    #This will convert the bestorf fasta file into a dict like: "name":"seq" and return it
    Dict={}
    for lines in fasta:
        if lines.startswith('>'):
            name=lines.strip('>\n')
            Dict[name]= '' 
        else:
            Dict[name] = Dict[name] + lines.upper()
    fasta.close()
    return Dict

def FASTAtoLargeDict(fulllist):
    #This will convert the shortilst fasta file into a dict like: "name":"seq" and return it
    LargeDict={}
    for lines in fulllist:
        if lines.startswith('>'):
            name=lines.strip('>\n')
            LargeDict[name]= '' 
        else:
            LargeDict[name] = LargeDict[name] + lines.upper()
    fulllist.close()
    return(LargeDict)

def BLASTparser(blast):
    blastuple = tuple(blast.readlines())
    blast.close()
    parsed = {}
    lock = 1
    for lines in blastuple:
        if lines.startswith('<b>Query='):
            title = re.search(' \w* ',lines).group(0)[1:-1]
            done = 0
        elif lines.startswith('>') and done == 0:
            anchor = re.search('= \d*',lines).group(0)[2:]
            lines = re.sub('<.* >','',lines).replace('</a>','')
            parsed[title] = lines.strip('\n> ') + '#' + anchor
            done = 1
        elif lines.startswith(' *****') and done == 0:
            parsed[title] = ''
            done = 1
    return(parsed)

def Characterize(Dict,Blasts,LargeDict,report):
    #Makes the SNP characterization and writes down the report.
    translate = { 'TTT': 'Phe', 'TCT': 'Ser', 'TAT': 'Tyr', 'TGT': 'Cys',
                  'TTC': 'Phe', 'TCC': 'Ser', 'TAC': 'Tyr', 'TGC': 'Cys',
                  'TTA': 'Leu', 'TCA': 'Ser', 'TAA': '***', 'TGA': 'Trp',
                  'TTG': 'Leu', 'TCG': 'Ser', 'TAG': '***', 'TGG': 'Trp',
                  'CTT': 'Leu', 'CCT': 'Pro', 'CAT': 'His', 'CGT': 'Arg',
                  'CTC': 'Leu', 'CCC': 'Pro', 'CAC': 'His', 'CGC': 'Arg',
                  'CTA': 'Leu', 'CCA': 'Pro', 'CAA': 'Gln', 'CGA': 'Arg',
                  'CTG': 'Leu', 'CCG': 'Pro', 'CAG': 'Gln', 'CGG': 'Arg',
                  'ATT': 'Ile', 'ACT': 'Thr', 'AAT': 'Asn', 'AGT': 'Ser',
                  'ATC': 'Ile', 'ACC': 'Thr', 'AAC': 'Asn', 'AGC': 'Ser',
                  'ATA': 'Met', 'ACA': 'Thr', 'AAA': 'Lys', 'AGA': 'Arg',
                  'ATG': 'Met', 'ACG': 'Thr', 'AAG': 'Lys', 'AGG': 'Arg',
                  'GTT': 'Val', 'GCT': 'Ala', 'GAT': 'Asp', 'GGT': 'Gly',
                  'GTC': 'Val', 'GCC': 'Ala', 'GAC': 'Asp', 'GGC': 'Gly',
                  'GTA': 'Val', 'GCA': 'Ala', 'GAA': 'Glu', 'GGA': 'Gly',
                  'GTG': 'Val', 'GCG': 'Ala', 'GAG': 'Glu', 'GGG': 'Gly'}
    report.write('''<HTML>
    <HEAD>
        <META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8">
        <TITLE>SNP Characterization</TITLE>            
        <STYLE>
        <!-- 
        BODY,DIV,TABLE,THEAD,TBODY,TFOOT,TR,TH,TD,P { font-family:"Arial"; font-size:small }
        -->
        </STYLE>                                               
    </HEAD>\n''')
    report.write('<BODY>\n<TABLE CELLSPACING=1 BORDER=1>\n<TBODY>\n<TR>\n')
    report.write('''<TD ALIGN=CENTER>Contig</TD>
        <TD ALIGN=CENTER>ORF Frame</TD>
        <TD ALIGN=CENTER>SNP Position in Contig</TD>
        <TD ALIGN=CENTER>ORF start</TD>
        <TD ALIGN=CENTER>ORF end</TD>
        <TD ALIGN=CENTER>ORF size</TD>
        <TD ALIGN=CENTER>SNP position in ORF</TD>
        <TD ALIGN=CENTER>Codon position</TD>
        <TD ALIGN=CENTER>Alternative codons</TD>
        <TD ALIGN=CENTER>Translations</TD>
        <TD ALIGN=CENTER>Silent?</TD>
        <TD ALIGN=CENTER>BLAST Reference</TD>
        <TD ALIGN=CENTER>BLAST Protein</TD>
        <TD ALIGN=CENTER>BLAST Species</TD>
        </TR>\n''')
    rows = []
    for k,v in Dict.items():
        snps = re.search('\{.*\}',k).group(0)
        tmpdict = eval(snps)
        v = v.replace('\n','')
        for ke,va in tmpdict.items():
            ke = ke - 1
            row = '<TR>\n<TD ALIGN=LEFT><a href="html_files/' + re.match('^\w*',k).group(0) + '.fasta">' + re.match('^\w*',k).group(0) + '</a></TD>\n'
            left_limit = re.search('\[.* -',k).group(0)[1:-2]
            right_limit = re.search('- .*\]',k).group(0)[2:-1]
            if int(left_limit) < int(right_limit):
                pos = int(left_limit) + ke
                div = (int(left_limit)/3)
                if str(div).endswith('0'):
                    frame = '3'
                elif str(div).endswith('3'):
                    frame = '1'
                else:
                    frame = '2'
            else:
                pos = int(left_limit) - ke
                div = (int(left_limit)/3)
                if str(div).endswith('0'):
                    frame = '-3'
                elif str(div).endswith('3'):
                    frame = '-1'
                else:
                    frame = '-2'
            row = row + '<TD ALIGN=CENTER>' + frame + '</TD>\n'
            row = row + '<TD ALIGN=CENTER>' + str(pos) + '</TD>\n'
            row = row + '<TD ALIGN=CENTER>' + left_limit + '</TD>\n'
            row = row + '<TD ALIGN=CENTER>' + right_limit + '</TD>\n' 
            row = row + '<TD ALIGN=CENTER><a href="html_files/' + k + '.ORF.fasta">' + str(abs(int(left_limit)-int(right_limit) + 1)) + '</TD>\n'
            row = row + '<TD ALIGN=CENTER>' + str(ke+1) + '</TD>\n'
            if str((ke+1)/3).find('.0') != -1:
                position = v[ke-2:ke+1]
                codons = list(v[ke-2:ke] + x for x in va)
                row = row + '<TD ALIGN=CENTER>3</TD>\n'
            elif str((ke+1)/3).find('.6') != -1:
                position = v[ke-1:ke+2]
                codons = list(v[ke-1:ke] + x + v[ke+1:ke+2] for x in va)
                row = row + '<TD ALIGN=CENTER>2</TD>\n'
            else:
                position = v[ke:ke+3]
                codons = list(x + v[ke+1:ke+3] for x in va)
                row = row + '<TD ALIGN=CENTER>1</TD>\n'
            translated = []
            for codon in codons:
                if codon in translate:
                    translated.append(translate[codon])
                else:
                    translated.append('ERR')
            row = row + '<TD ALIGN=CENTER>' + str(codons).replace('\'','').replace(', ','|') + '</TD>\n'
            row = row + '<TD ALIGN=CENTER>' + str(translated).replace('\'','').replace(', ','|') + '</TD>\n'
            silent = set(translated)
            if len(silent) == 1:
                row = row + '<TD ALIGN=CENTER>Y</TD>\n'
            else:
                row = row + '<TD ALIGN=CENTER>N</TD>\n'
            if re.match('^\w*',k).group(0) in Blasts and Blasts[re.match('^\w*',k).group(0)] != '':
                reference = re.match('^.*\|.*\|',Blasts[re.match('^\w*',k).group(0)]).group(0)
                protein = re.sub('^.*\|.*\|','',Blasts[re.match('^\w*',k).group(0)])
                if '[' in Blasts[re.match('^\w*',k).group(0)]:
                    protein = re.search('^.*\[',protein).group(0)[:-1]
                    species = re.search('\[.*#',Blasts[re.match('^\w*',k).group(0)]).group(0).strip('[]')[:-2]
                else:
                    protein =  re.search('^.*#',protein).group(0)[:-1]
                    species = 'N/A'
                row = row + '<TD ALIGN=LEFT><a href="html_files/ORFblast.html' + re.search('#\d*$',Blasts[re.match('^\w*',k).group(0)]).group(0) + '">' + reference + '</a></TD>\n'
                row = row + '<TD ALIGN=LEFT>' + protein + '</TD>\n'
                row = row + '<TD ALIGN=LEFT>' + species + '</TD></TR>\n'
            else:
                row = row + '<TD ALIGN=LEFT>No similar proteins found in database</TD><TD>N/A</TD><TD>N/A</TD></TR>\n'
            rows.append(row)
    rows.sort()
    for r in rows:
        report.write(r)
    report.write('<TR><TH ALIGN=CENTER COLSPAN="14">Contigs that contained SNPs that could not be characterized since they were outside any ORF</TH></TR>')
    tester = set(re.match('^\w*',x).group(0) for x in Dict.keys())
    for unchar in LargeDict:
        if re.match('^\w*',unchar).group(0) not in tester:
            report.write('<TR>\n<TH ALIGN=LEFT COLSPAN="14">' + '<a href="html_files/' + re.match('^\w*',unchar).group(0) + '.fasta">' + re.match('^\w*',unchar).group(0) + '</a>''</TH>\n</TR>\n')
    report.write('</TBODY>\n</TABLE>\n</BODY>\n</HTML>')
    report.close()

def FASTAsplitter(Dict,LargeDict,report_file):
    #This will split the Dict with the relevant FASTA information into individual fasta files for viewing
    filespath = os.path.split(report_file)[0] + '/html_files/'
    try:
        os.mkdir(filespath)
    except:
        print('Warning - directory ' + filespath + '/html_files exists')
    for seqs in LargeDict:
        smallfile = open(filespath + re.match('^\w*',seqs).group(0) + '.fasta','w')
        smallfile.write('>' + seqs + '\n')
        smallfile.write(LargeDict[seqs])
        smallfile.close()
    for seqs in Dict:
        smallfile = open(filespath + seqs + '.ORF.fasta','w')
        smallfile.write('>' + seqs + '\n')
        smallfile.write(Dict[seqs])
        smallfile.close()

def RunModule(fasta_file,fulllist_file,blast_file,report_file):
    fasta = open(fasta_file,'r')
    fulllist = open(fulllist_file,'r')
    blast = open(blast_file,'r')
    report = open(report_file,'w')

    Dict=FASTAtoDict(fasta)
    LargeDict=FASTAtoLargeDict(fulllist)
    Blasts=BLASTparser(blast)
    Characterize(Dict,Blasts,LargeDict,report)
    FASTAsplitter(Dict,LargeDict,report_file)