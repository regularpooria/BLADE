from pandas import read_csv

text="""
youtube-dl-1  | youtube-dl,1,buggy,pass
youtube-dl-1  | youtube-dl,2,buggy,pass
youtube-dl-1  | youtube-dl,3,buggy,pass
youtube-dl-1  | youtube-dl,5,buggy,fail
youtube-dl-1  | youtube-dl,6,buggy,pass
youtube-dl-1  | youtube-dl,7,buggy,fail
youtube-dl-1  | youtube-dl,8,buggy,pass
youtube-dl-1  | youtube-dl,9,buggy,pass
youtube-dl-1  | youtube-dl,10,buggy,fail
youtube-dl-1  | youtube-dl,11,buggy,pass
youtube-dl-1  | youtube-dl,12,buggy,pass
youtube-dl-1  | youtube-dl,13,buggy,fail
youtube-dl-1  | youtube-dl,14,buggy,fail
youtube-dl-1  | youtube-dl,15,buggy,fail
youtube-dl-1  | youtube-dl,16,buggy,pass
youtube-dl-1  | youtube-dl,17,buggy,pass
youtube-dl-1  | youtube-dl,18,buggy,pass
youtube-dl-1  | youtube-dl,19,buggy,pass
youtube-dl-1  | youtube-dl,20,buggy,fail
youtube-dl-1  | youtube-dl,21,buggy,pass
youtube-dl-1  | youtube-dl,22,buggy,pass
youtube-dl-1  | youtube-dl,23,buggy,fail
youtube-dl-1  | youtube-dl,24,buggy,pass
youtube-dl-1  | youtube-dl,25,buggy,pass
youtube-dl-1  | youtube-dl,26,buggy,fail
youtube-dl-1  | youtube-dl,27,buggy,pass
youtube-dl-1  | youtube-dl,28,buggy,fail
youtube-dl-1  | youtube-dl,29,buggy,pass
youtube-dl-1  | youtube-dl,30,buggy,pass
youtube-dl-1  | youtube-dl,31,buggy,pass
youtube-dl-1  | youtube-dl,32,buggy,pass
youtube-dl-1  | youtube-dl,33,buggy,pass
youtube-dl-1  | youtube-dl,35,buggy,pass
youtube-dl-1  | youtube-dl,36,buggy,pass
youtube-dl-1  | youtube-dl,38,buggy,pass
youtube-dl-1  | youtube-dl,39,buggy,pass
"""


print(text.count("pass") / (text.count("pass") + text.count("fail")))