#!/usr/bin/env python3

import argparse, gzip, re, sys

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-fai',  '--fai-file',   type=str,  help='.fa.fai file',  required=True,  default=None)
parser.add_argument('-beds', '--bed-files',  type=str,  help='BED files', nargs='*', required=True,  default=None)
parser.add_argument('-out ', '--bed-out',    type=str,  help='BED file out', required=False,  default=sys.stdout)

args = parser.parse_args()

fai_file  = args.fai_file
bed_files = args.bed_files
bed_out   = args.bed_out


def fai2bed(file_name):
        
    with open(file_name) as gfile:
        line_i = gfile.readline().rstrip('\n')
        
        callableLociBoundries = {}
        callableLociCounters  = {}
        orderedContig = []
        while line_i:
            
            contig_match = re.match(r'([^\t]+)\t', line_i)

            if contig_match:
                
                contig_i = contig_match.groups()[0].split(' ')[0]  # some .fai files have space after the contig for descriptions.
                orderedContig.append( contig_i )
                
                contig_size = int( line_i.split('\t')[1] )
                
                callableLociBoundries[contig_i] = [0, contig_size ]
                callableLociCounters[contig_i] = [0]
                
            else:
                raise Exception('.fai file format not as expected.')
            
            line_i = gfile.readline().rstrip('\n')
            
    return callableLociBoundries, callableLociCounters, orderedContig



def collapseIdenticalBoundries(boundries, counters):
    
    assert len(boundries) == len(counters) + 1
    
    outBoundries = []
    outCounters  = []
    
    outBoundries.append( boundries[0] )
    
    i = 0
    while i <= len(boundries) - 2:
        j = i + 1
        
        if boundries[i] != boundries[j]:
            outBoundries.append( boundries[j] )
            outCounters.append( counters[j-1] )
        
        i += 1
        
    return outBoundries, outCounters



def countIntersectedRegions(original_boundry, original_counter, additional_region):
    
    bedStart = additional_region[0]
    bedEnd   = additional_region[1]
    
    newBoundry = []
    newCounter  = []
    ith_boundry = 0
        
    region_iterator = iter(original_boundry)
    boundry_i = next(region_iterator)
    
    # Add the preceding positions before hitting the added region
    while boundry_i < bedStart:
        
        newBoundry.append( boundry_i )
            
        if ith_boundry + 1 < len(original_boundry):
            newCounter.append( original_counter[ith_boundry] )
                
        ith_boundry += 1
        boundry_i = next(region_iterator)
    
    # Insert the added start position:
    newBoundry.append( bedStart )
    
    if ith_boundry -1 + 1 < len(original_boundry):
        newCounter.append( original_counter[ith_boundry-1] + 1)
        
    # Add original boundries if they're no greater than the end position
    while boundry_i < bedEnd:
        
        newBoundry.append( boundry_i )

        if ith_boundry + 1 < len(original_boundry):
            newCounter.append( original_counter[ith_boundry] + 1)
                
        ith_boundry += 1
        boundry_i = next(region_iterator)
    
    # Add the end position:
    ith_boundry = ith_boundry - 1
    newBoundry.append( bedEnd )
    if ith_boundry + 1 < len(original_boundry):
        newCounter.append( original_counter[ith_boundry])
        ith_boundry += 1
    
    # Add the boundry that passed the bedEnd:
    newBoundry.append( boundry_i )
    if ith_boundry + 1 < len(original_boundry):
        newCounter.append( original_counter[ith_boundry] )
        ith_boundry += 1
    
    # Add the rest:
    for boundry_i in region_iterator:
        newBoundry.append( boundry_i )
        if ith_boundry + 1 < len(original_boundry):
            newCounter.append( original_counter[ith_boundry] )
        
        ith_boundry += 1
    
    consolidatedBoundries, consolidatedCounters = collapseIdenticalBoundries(newBoundry, newCounter)
    
    return consolidatedBoundries, consolidatedCounters
        
        

# Start routine:
contigBoundries, contigCounters, orderedContigs = fai2bed(fai_file)

for bed_file_i in bed_files:
    
    with open(bed_file_i) as bed_i:
        
        line_i = bed_i.readline().rstrip()
        
        while line_i:
            item = line_i.split('\t')
        
            chrom  = item[0]
            region = int( item[1] ), int( item[2] ) + 1
        
            contigBoundries[chrom], contigCounters[chrom] = countIntersectedRegions(contigBoundries[chrom], contigCounters[chrom], region)
            
            line_i = bed_i.readline().rstrip()



for contig_i in orderedContigs:
    
    if contigCounters[ contig_i ] != [0]:
        
        for i, count_i in enumerate( contigCounters[contig_i] ):
            
            out_string = '{}\t{}\t{}\t{}'.format(contig_i, contigBoundries[contig_i][i], contigBoundries[contig_i][i+1]-1, count_i)
            
            bed_out.write(out_string + '\n')
