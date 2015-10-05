import numpy
import sys
import time

from model.nn_model import Model
import training_data_gen.utils as utils
from training_data_gen.training_data_generator import TrainingData

def IterateMinibatches(inputs, targets, batch_size, shuffle=False):
    assert len(inputs) == len(targets)
    if shuffle:
        indices = numpy.arange(len(inputs))
        numpy.random.shuffle(indices)
    for start_idx in range(0, len(inputs) - batch_size + 1, batch_size):
        if shuffle:
            excerpt = indices[start_idx:start_idx + batch_size]
        else:
            excerpt = slice(start_idx, start_idx + batch_size)
        yield inputs[excerpt], targets[excerpt]


BATCH_SIZE = 5000


def Train(train_fn, image_input, target_chars, batch_size=BATCH_SIZE):
  train_err = 0
  train_batches = 0
  start_time = time.time()
  print("Training")
  for image_input_batch, target_chars_batch in IterateMinibatches(
      image_input, target_chars, batch_size, shuffle=False):
    batch_start_time = time.time()
    train_err += train_fn(image_input_batch, target_chars_batch)
    train_batches += 1
    print("Batch training took {:.3f}s".format(time.time() - batch_start_time))
    print("  training loss:\t\t{:.6f}".format(train_err / train_batches))

  # Then we print the results for this epoch:
  print("Training took {:.3f}s".format(time.time() - start_time))
  print("  training loss:\t\t{:.6f}".format(train_err / train_batches))


def Test(test_fn, image_input, target_chars, batch_size=BATCH_SIZE):
  test_err = 0
  test_acc = 0
  test_batches = 0
  start_time = time.time()
  for image_input_batch, target_chars_batch in IterateMinibatches(
      image_input, target_chars, batch_size, shuffle=False):
    test_prediction, err, acc = test_fn(image_input_batch, target_chars_batch)
    test_err += err
    test_acc += acc
    test_batches += 1

  print("Testing took {:.3f}s".format(time.time() - start_time))
  print("  loss:\t\t{:.6f}".format(test_err / test_batches))
  print("  accuracy:\t\t{:.2f} %".format((test_acc / test_batches) * 100))


def Run(training_data_dir, val_data_file, test_data_file, model_save_path, num_epochs=20):
  print('Compiling model')
  captcha_model = Model()
  print('Loading validation data')
  val_image_input, val_target_chars = TrainingData.Load(val_data_file)
  val_image_input = val_image_input[:BATCH_SIZE]
  val_target_chars = val_target_chars[:BATCH_SIZE]
  print('Starting training')
  for epoch_num in range(num_epochs):
    for i, training_file in enumerate(
        utils.GetFilePathsUnderDir(training_data_dir, shuffle=False)):
      image_input, target_chars = TrainingData.Load(training_file)
      Train(captcha_model.GetTrainFn(), image_input, target_chars)

      Test(captcha_model.GetTestFn(), image_input[:BATCH_SIZE], target_chars[:BATCH_SIZE])
      Test(captcha_model.GetTestFn(), val_image_input, val_target_chars)
      if i != 0 and i % 10 == 0:
        print 'Processed {0} training files.'.format(i)

  test_image_input, test_target_chars = TrainingData.Load(test_data_file)
  captcha_model.SaveModelParamsToFile(model_save_path)


if __name__ == '__main__':
  Run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])