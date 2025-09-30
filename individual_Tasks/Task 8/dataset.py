# dataset.py
# Ordered list of 28 students (roll, name) exactly taken from the pic (starts at 23102A0055).
from math import ceil
import random

STUDENTS = [
    ("23102A0055", "SHRAVANI CHAVAN"),
    ("23102A0056", "SOHAN KUMAR"),
    ("23102A0057", "NIKHIL PATIL"),
    ("23102A0058", "HUSSAIN ANAJWALA"),
    ("23102A0059", "SAISH MORE"),
    ("23102A0060", "KETKI GAIKWAD"),
    ("23102A0061", "SAHIL GHOGARE"),
    ("23102A0062", "KHUSHBOO YADAV"),
    ("23102A0063", "VAISHNAVI SAWANT"),
    ("23102A0064", "SOHAM KHOLAPURE"),
    ("23102A0065", "KHUSHAL SOLANKI"),
    ("23102A0068", "DIKSHA PARULEKAR"),
    ("23102A0069", "DEVANSHI MAHAJAN"),
    ("23102A0070", "BHUMI NAIK"),
    ("23102A0071", "YASHRAJ PATIL"),
    ("23102A0072", "SHRUTI TAMBAD E"),
    ("23102A0073", "MOHAMMAD EQUAAN KACCHI"),
    ("23102A0074", "VAISHNAVI KHOPKAR"),
    ("23102A0075", "HASNAIN KHAN"),
    ("23102A0076", "PRASANA SHANGLOO"),
    ("24102A2001", "SIDDHI GAWADE"),
    ("24102A2002", "SANDEEP MAJUMDAR"),
    ("24102A2003", "CHIRAG CHAUDHARI"),
    ("24102A2004", "ANUSHKA UNDE"),
    ("24102A2005", "SAJIYA SHAIKH"),
    ("24102A2006", "TAMANNA SHAIKH"),
    ("24102A2007", "TANISHQ KULKARNI"),
    ("24102A2008", "ARAV MAHIND"),
]

def generate_marks(seed: int = 42, isa_range=(0,15), mse_range=(0,20), ese_range=(0,40)):
    rnd = random.Random(seed)
    rows = []
    for rn, name in STUDENTS:
        isa = rnd.randint(*isa_range)
        mse = rnd.randint(*mse_range)
        ese = rnd.randint(*ese_range)
        total = isa + mse + ese
        rows.append({
            "rn": rn,
            "name": name,
            "isa": isa,
            "mse": mse,
            "ese": ese,
            "total": total
        })
    return rows

def chunkify(rows, chunk_size=7):
    n = len(rows)
    num_chunks = ceil(n / chunk_size)
    chunks = []
    for i in range(num_chunks):
        start = i * chunk_size
        chunks.append(rows[start:start+chunk_size])
    return chunks
