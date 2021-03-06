cloudml Package
================

**\[WIP\]**

The **cloudml** package provides an R interface to the Google Cloud Machine Learning platform. **cloudml** makes it easy to take machine learning applications built with R packages like [tensorflow](https://tensorflow.rstudio.com/), [Keras](https://keras.rstudio.com/), and [tfestimators](https://tensorflow.rstudio.com/tfestimators/), and use Google Cloud's machine learning platform for training, testing, and prediction.

Workflow
--------

The **cloudml** package seeks to automate the process of taking a machine learning model, and training / testing / predicting with that model on Google Cloud. We're aiming for an iterative workflow of the form:

1.  Start by building a TensorFlow application that trains and runs locally on sample data.
2.  Tweak the application to accept model inputs through the use of configurable [flags](https://tensorflow.rstudio.com/tools/training_flags.html),
3.  Generate a `flags.yml` file that encodes the different training parameters to be used in your cloud training configuration,
4.  Use the various **cloudml** APIs to request this training of your model on Google Cloud.

We'll use the [census example](https://github.com/rstudio/cloudml/tree/master/examples/census) as we walk through the steps needed to get set up with Google Cloud. We use this application to build a model that predicts an individual's income category using the United Stated Census Income Dataset.

Setting Up
----------

Before using the **cloudml** package, you'll need to make sure you're set up with an account and project on Google Cloud. In addition, the **cloudml** package makes use of the [Google Cloud SDK](https://cloud.google.com/sdk/) for communication with the Google Cloud machine learning platform. You can follow the instructions [here](https://cloud.google.com/sdk/downloads) to get the SDK installed on your machine.

Each **cloudml** application needs to be associated with an Google Cloud project + account. If you haven't already, you can [create an account](https://console.cloud.google.com) following the instructions online, and then [create a project](https://cloud.google.com/resource-manager/docs/creating-managing-projects) after that. You'll also want to provision a [bucket](https://cloud.google.com/storage/docs/creating-buckets), to be used as a storage / staging space for applications trained in the cloud.

After you've set this up, you might want to set up a default configuration for this account and project. You can do this from the command line with:

    gcloud config set core.account <account>
    gcloud config set core.project <project>

We'll show later how you can configure an application to deploy to multiple accounts / projects if so desired.

Authentication
--------------

After creating your account, you'll need to set up default application credentials to ensure that the Google Cloud SDK can securely communicate with Google and take actions with your project. Try running

    gcloud auth application-default login

from a terminal, to request these credentials.

Configuration
-------------

Application deployment is configured through the use of a top-level [YAML](http://yaml.org/) file called `cloudml.yml`. See [here](https://github.com/rstudio/cloudml/blob/master/examples/census/cloudml.yml) for the associated file used in our census example -- we'll explore the fields used here.

    ## gcloud:
    ##   project         : "rstudio-cloudml"
    ##   account         : "kevin@rstudio.com"
    ##   region          : "us-central1"
    ##   runtime-version : "1.2"
    ## 
    ## cloudml:
    ##   storage         : "gs://rstudio-cloudml/census"

The `gcloud` key is used for configuration specific to the Google Cloud SDK, and so contains items relevant to how applications are deployed.

-   Any deployments made will be associated with the `project` and `account` fields above,

-   Instances provisioned for training will be launched in the region specified by `region`,

-   The TensorFlow version to be used during training is configured using the `runtime-version` field.

The `storage` field in the `cloudml` section indicates where various artefacts used during provisioning and training are stored. Some useful paths to know:

-   `<storage>/staging`: applications will be 'staged' in this directory; that is, your deployed application will be uploaded and built in this location;

-   `<storage>/runs/<timestamp>`: training outputs will be copied to this directory.

Deployment
----------

If you've followed these steps, your application should now be ready to be deployed to Google Cloud.

### Training

You can train your application with:

``` r
job <- cloudml::cloudml_train(entrypoint = "train.R")
```

This function will submit your application to Google Cloud, and request that it train your application by sourcing the training script `"train.R"`. You should see output of the form:

    > job <- with_census(cloudml::cloudml_train())
    Job 'census_cloudml_2017_10_26_172932520' successfully submitted.

    Check status and collect output with:
    - job_status("census_cloudml_2017_10_26_172932520")
    - job_collect("census_cloudml_2017_10_26_172932520")

    View job in the Cloud Console at:
    https://console.cloud.google.com/ml/jobs/census_cloudml_2017_10_26_172932520?project=rstudio-cloudml

    View logs at:
    https://console.cloud.google.com/logs?resource=ml.googleapis.com%2Fjob_id%2Fcensus_cloudml_2017_10_26_172932520&project=rstudio-cloudml

After submitting this job, you can tell the R session to wait for training to complete, and pull the generated models back to your local filesystem with:

``` r
collected <- cloudml::job_collect(job)
```

The R session will wait and continue polling Google Cloud until your application has finished running; if the application trained successfully, then the trained models will be copied to disk.

**TODO**: <https://cloud.google.com/ml-engine/docs/prediction-overview> suggests that one may need to explicitly call into [SavedModel](https://www.tensorflow.org/api_docs/python/tf/saved_model) APIs to produce a model that can be used for prediction.

> The "model" that you deploy to Cloud ML Engine as a model version is a TensorFlow SavedModel. You export a SavedModel in your trainer. It doesn't matter whether you trained your model in the cloud using Cloud ML Engine or elsewhere as long as you have a SavedModel with the serving signature set to serving\_default.

### Prediction

**TODO**:

    gcloud ml-engine jobs submit prediction <job> \
        --model-dir <model-dir>                   \
        --data-format <tf-record>                 \
        --input-paths <paths>

### Models

**TODO**:

Define a model (give it a name): - `gcloud ml-engine models create <model>`

Assign a particular instance of a model a version: - `gcloud ml-engine versions create <version> --model <model> --origin <model-dir>`

Use that model for prediction: - `gcloud ml-engine predict --model <model> --version <version>`
