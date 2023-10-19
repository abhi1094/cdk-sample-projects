Can I make AWS clients (AmazonRekognition) static members of Lambda handler ? Are they thread safe among requests ?


Does AmazonRekognition use different ML algorithms to detect faces in different methods : detectLabels, detectFaces, indexFaces, because seamns that returns different results ?

Are there some best practices for the values of the Confidence of Rekognition Labels ? 
For example, when calculating the Dominant Label for a picture, which Labels should be considered (the minimum Confidence) ?


Can you talk a bit about how to use EKS for long-running heavy compute jobs? Alternatively, is there something more suitable given that Kubernetes is meant more for lighter, stateless workloads?
