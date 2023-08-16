# Rule formats

## For Rules (Library) not listed below

The API config is simply the API names

## For Rule 3, 4, 5, 13, 14:

### Meaning:

API1-API2

The rules need a pair of APIs to build equivalent graphs. It may use API2 to implement the functionality of API1, or apply API1 and API2 in sequence to generate output equivalent to input.

### Examples:

For rule 3: torch.nn.Conv2d-torch.nn.Conv3d.

It means to use torch.nn.Conv3d to implement the functionality of torch.nn.Conv2d

## For Rule 8 pytorch - sparse:

### Dash - is delimiter 

### Underscore _ is the start of API (potential bug: if there is _ in API name

### Meaning: 

SparseAPI-sparseInputs_nonSparseAPI-sparseInputs-[mappingArg1-mappingArg2]

### Examples:

torch.sspaddmm-input-mat1_torch.sparse.addmm-mat1_input-mat

It means there's a pair of APIs: torch.sspaddmm, and its sparse arguments are input and mat1; and torch.sparse.addmm, and its sparse argument is mat1. "input-mat" is the argument mapping since the API torch.sparse.addmm doesn't have input argument. Instead, it has mat argument. Therefore we need to update the argument name when we apply the input of torch.sspaddmm to torch.sparse.addmm.

## For Rule 8 tensorflow - sparse:

### Meaning: 

API-sparseInput

### Examples:

tf.sparse.sparse_dense_matmul-sp_a

It means the API tf.sparse.sparse_dense_matmul has an arguement sp_a which should be a sparse tensor.

## For Rule 10 tensorflow - time major:

### Meaning: 

API-cell-bidirectional

### Examples:

tf.keras.layers.LSTM-None-True

It means the API is tf.keras.layers.LSTM, and there's no cell function. (Cell function is a special arguement for API tf.keras.layers.RNN). True indicates we need to add bidirectional layers to the API.

tf.keras.layers.RNN-tf.keras.layers.GRUCell-False

It means the API is tf.keras.layers.RNN, and it uses tf.keras.layers.GRUCell as its cell function. False indicates we don't add bidirectional layers to the API.

## For Rule 12 - data type:

### Meaning: 

API-Input-srcType-dstType

### Examples:

tf.transpose-a-tf.float32-tf.float64

It means for API tf.transpose, we first execute it with its argument a of data type tf.float32. Then we execute it with its argument a convereted to data type tf.float64 (the value is the same).

## For Rule 15 pytorch - batch size:

### Meaning: 

model-input-s1-s2

### Examples:

torchvision.models.resnet18-input_pt_0-60-44

It means for model torchvision.models.resnet18, we select input_pt_0 as its input file. We need separate input files for different models because the inputs have already been preprocessed according to the model type. 60 and 44 represents two batch size s1, s2 which we will use to evaluate the model on the inputs.

## For Rule 15 tensorflow - batch size:

### Meaning: 

model-input-optimizer-loss-metrics-s1-s2

### Examples:

model_14-input_14-adam-categorical_crossentropy-Accuracy-56-32

It means we compile model_14 (ResNet50V2) with adam as its optimizer, with categorical_crossentropy as its loss function and setting metrics to Accuracy. Then we evaluate it on input_14 file for batch size 56 and 32 respectively.

## For Rule 16 pytorch - model save and load:

### Meaning: 

model-input-mode

### Examples:

torchvision.models.resnet18-input_pt_0-model

It means for model torchvision.models.resnet18, we select input_pt_0 as its input file. We save the entire model and then load it back.

## For Rule 16 tensorflow - model save and load:

### Meaning: 

model-input-optimizer-loss-metrics-mode

### Examples:

model_14-input_14-adam-categorical_crossentropy-Accuracy-weight

It means we compile model_14 (ResNet50V2) with adam as its optimizer, with categorical_crossentropy as its loss function and setting metrics to Accuracy. Then we save the model's weight to disk and load it. For model config, we copy it in the memory directly. 