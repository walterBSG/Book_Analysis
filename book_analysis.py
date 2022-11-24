import io
import os
import re
import nltk
import scipy
import PyPDF2
import itertools
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import community
from collections import Counter
from pyvis.network import Network
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

def removeElements(lst, k):
    counted = Counter(lst)
    temp_lst = []
    
    for el in counted:
        if counted[el] < k:
            temp_lst.append(el)
    res_lst = []
    
    for el in lst:
        if el not in temp_lst:
            res_lst.append(el)
    return(res_lst)

def getNames(text):
    nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
    names = []
    for nltk_result in nltk_results:
        if type(nltk_result) == Tree:
            name = ''
            for nltk_result_leaf in nltk_result.leaves():
                name += nltk_result_leaf[0] + ' '
            if nltk_result.label() == 'PERSON':
                names.append(name.replace(' ', ''))
    names = removeElements(names, 5)
    names = list(dict.fromkeys(names))
    return names

def getRelations(text, names, reach = 9):
    relations = []
    filteredlines = []
    
    for line in text:
        linenames = [n for n in line.split(' ') if n in names]
        filteredlines.append(linenames)
    
    for i in range(len(filteredlines)-1):
        end = min(i+reach, len(filteredlines)-1)
        relation = sorted(sum(filteredlines[i:end], []))
        relations += list(itertools.combinations(dict.fromkeys(relation), 2))

    relations = [rel for rel in relations if len(rel)>1]
    relations.sort()
    return relations

def getBooks():
    filenames = next(os.walk('Books'), (None, None, []))[2]
    books = [open('Books/'+file).read() for file in filenames]
    return books, filenames

def filterText(text):
    text = text.replace("\n",'').replace("\'",'')
    text = re.split('\. |! |\? ',text)
    text = list(filter(None, text))
    return text

def createGraph(df, name):
    g = nx.from_pandas_edgelist(df, source='N1', target='N2', edge_attr='value', edge_key=None, create_using = nx.Graph())
    plt.figure(figsize=(10,10))
    net = Network(notebook = True, width="1500px", height="1200px", bgcolor='#222222', font_color='white')
    net.repulsion()
    node_degree = dict(g.degree)
    com = community.best_partition(g)
    nx.set_node_attributes(g, node_degree, 'size')
    nx.set_node_attributes(g, com, 'group')
    net.from_nx(g)
    net.show("img/{}_graph.html".format(name))
    return df

def grafRelations(relations, name):
    df = dict(Counter(relations))
    df = [[key[0], key[1], df[key]] for key in df.keys()]
    df = pd.DataFrame(df, columns = ['N1', 'N2', 'value'])
    createGraph(df, name)
    return df

def analiseBooks(books, booknames):
    for book, bookname in zip(books, booknames):  
        names = getNames(book)
        book = filterText(book)
        relations = getRelations(book, names)
        grafRelations(relations, bookname)
        
    return
        

def main():
    books, booknames = getBooks()
    analiseBooks(books, booknames)

if __name__ == '__main__':
    main()