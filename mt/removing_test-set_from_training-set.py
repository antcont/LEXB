'''
Getting (new) training set by subtracting (old) test set to (new) total dataset.
Input and output are txt newline-separated lines of tab-separated sentences

Use it when test set has been modified/corrected and we need an up-to-date training test,
and when new data is added to training set.
'''


total_dataset = r""
test_set_path = r""
reference_path = r""
training_set_output = r""

with open(total_dataset, "r", encoding="utf-8") as data:
    dataset = data.read().splitlines()

with open(test_set_path, "r", encoding="utf-8") as test:
    test_set = test.read().splitlines()

with open(reference_path, "r", encoding="utf-8") as ref:
    reference = ref.read().splitlines()

# checking test and ref have same length
if len(test_set) != len(reference):
    print("Error: test and reference have different lengths.")
    exit()

bi_test_set = []
# create bilingual test_set lines with tab-separated sentence pairs
for i in range(len(test_set)):
    bi_test_set.append(test_set[i] + "\t" + reference[i])

# creating new training set
training_set = []
for TU in dataset:
    if TU not in bi_test_set:
        training_set.append(TU)
    #else:
        #print("Error: test set segment not found in the original dataset. Couldn't remove it from the training set.")

print(len(dataset))
print(len(bi_test_set))
print(len(training_set))

#export new training set
training = "\n".join(training_set)
with open(training_set_output, "w", encoding="utf-8") as tr:
    tr.write(training)

print("Done.")