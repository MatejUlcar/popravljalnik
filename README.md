# popravljalnik
Code for generating, correcting, modelling grammatical mistakes in Slovene

## Generation
`generiranje_napak.py` generates various subcategories of mistakes in the category `O/KAT` of the Šolar 3.0 corpus corrections categorization. 
The code assumes input corpus in `.conllu` format. 
So far, we have used corpus MAKS to generate mistakes from. 

## TODO
* The paths are hard-coded, generalize.
* Expand the code to cover other subcategories of corrections.
* Add the model training and evaluation code.
