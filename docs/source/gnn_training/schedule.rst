Graph Neural Network Training
*****************************

Training Parameters
___________________

.. list-table:: Hyper-Parameter Schedule
   :header-rows: 1

   * - Name
     - Optimizer
     - Optimizer-Params
     - Scheduler
     - Scheduler-Params
     - BatchSize

   * - MRK1
     - ADAM
     - lr: 0.001, wd: 0.001
     - /
     - /
     - 10

   * - MRK2
     - ADAM
     - lr: 0.001, wd: 0.001
     - /
     - /
     - 50 

   * - MRK3
     - ADAM
     - lr: 0.001, wd: 0.001
     - /
     - /
     - 100

   * - MRK4
     - ADAM
     - lr: 0.001, wd: 0.001
     - /
     - /
     - 200


   * - MRK5
     - ADAM
     - lr: 0.001, wd: 0.001
     - /
     - /
     - 10

   * - MRK6
     - ADAM
     - lr: 0.0001, wd: 0.001
     - /
     - /
     - 50 

   * - MRK7
     - ADAM
     - lr: 0.001, wd: 0.0001
     - /
     - /
     - 100

   * - MRK8
     - ADAM
     - lr: 0.0001, wd: 0.0001
     - /
     - /
     - 200

   * - MRK9
     - ADAM
     - lr: 0.0001, wd: 0.001
     - ExponentialLR
     - 0.5
     - 10

   * - MRK10
     - ADAM
     - lr: 0.001, wd: 0.0001
     - ExponentialLR
     - 1.0
     - 50 

   * - MRK11
     - ADAM
     - lr: 0.0001, wd: 0.0001
     - ExponentialLR
     - 2.0
     - 100

   * - MRK12
     - ADAM
     - lr: 0.0001, wd: 0.0001
     - ExponentialLR
     - 4.0
     - 200

   * - MRK13
     - ADAM
     - lr: 0.0001, wd: 0.001
     - CyclicLR
     - 0.0001
     - 10

   * - MRK14
     - ADAM
     - lr: 0.001, wd: 0.0001
     - CyclicLR
     - 0.001
     - 50 

   * - MRK15
     - ADAM
     - lr: 0.0001, wd: 0.0001
     - CyclicLR
     - 0.01
     - 100

   * - MRK16
     - ADAM
     - lr: 0.0001, wd: 0.0001
     - CyclicLR
     - 0.1
     - 200


   * - MRK17
     - SGD
     - lr: 0.0001, wd: 0.001
     - momentum: 0.0001
     - /
     - 10

   * - MRK18
     - SGD
     - lr: 0.001, wd: 0.0001
     - momentum: 0.0005
     - /
     - 50 

   * - MRK19
     - SGD
     - lr: 0.0001, wd: 0.0001
     - momentum: 0.001
     - /
     - 100

   * - MRK20
     - SGD
     - lr: 0.0001, wd: 0.0001
     - 0.0015
     - /
     - 200
