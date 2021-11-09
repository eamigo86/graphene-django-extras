#!groovy

@Library('shared-library') _
import quarticpipeline.PipelineBuilder

containerNodes = [
  Publish: [
    dir: './jenkins_scripts/',
      steps: [
        publish: [
          file_name: 'publish.sh',
            ]
        ]
    ]
]

pipelineBuilder = new PipelineBuilder(this, env, scm, containerNodes)
userEnv = ['RESERVE=azubuntu']

pipelineBuilder.executePipeline(userEnv)
