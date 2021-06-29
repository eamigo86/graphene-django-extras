@Library('shared-library') _
import quarticpipeline.PipelineBuilder

containerNodes = [
  Publish: [
    dir: './jenkins_scripts/',
      steps: [
        publish: [
          file_name: 'publish.sh',
          docker_image: 'quarticai/python:3.9.5-slim',
          docker_image_args: '-u root'
            ]
        ]
    ]
]

pipelineBuilder = new PipelineBuilder(this, env, scm, containerNodes)
userEnv = ['RESERVE=azubuntu']

pipelineBuilder.executePipeline(userEnv)
