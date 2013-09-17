Our Method
================

`Locked-in Syndrome (LIS) <http://en.wikipedia.org/wiki/Locked-In_syndrome>`_
is a neurological condition characterized
by the loss of most or all motor control while retaining cognitive functions.
As a consequence, locked-in individuals are unable to interact physically
with their environment and have limited or no means to communicate.
Brain Computer Interfaces (BCIs) offer a method for locked-in patients
to communicate with others and to manipulate their surroundings.

Brain-computer interfaces require three main components.
The first is a brain function or brain wave to monitor and study.
This is a brain process that can be controlled or manipulated by the user in order to use the BCI.
Some examples of this are `Sensorimotor Rhythms (SMR) <http://en.wikipedia.org/wiki/Sensorimotor_rhythm>`_
and `Event-related potentials (ERP) <http://en.wikipedia.org/wiki/Event-related_potential>`_.
SMR is a signal created in the primary motor cortex during intended limb motion.
An ERP, such as P300, is a signal created in the parietal lobe in response to
very specific visual stimulus, surrounded by non-important ones.
The signals that we control with our BCI are Steady-State Visually-Evoked Potentials (SSVEP).
SSVEPs are brain waves of the occipital lobe that are created when a user attends to a
flashing light at a given frequency. The SSVEP reaches the occipital lobe at the same frequency
and first harmonic of the flashing stimulus. For our purposes, we have tested with
flashing light-emitting diodes (LED) and flashing rectangles on a computer monitor

The second component of any BCI is a method of acquiring and decoding brain functions
Brain activity can be acquired by either invasive or non-invasive means.
Invasive means require the opening of the skull to implant electrodes on the surface, or
into the surface of the brain.
This method provides high spatial resolution, but requires surgery and adds the risk of infection and damage to the neural tissue.
Non-invasive means such as Electro-encephalograpy (EEG) have lower spatial resolution, but excellent temporal resolution, and no
risk of injury.
EEG is used for this project to record SSVEP from the occipital lobe of the user.
EEG is usually decoded using a `Fast-Fourier Transform (FFT) <http://en.wikipedia.org/wiki/FFT>`_,
although their are other methods for decoding such as
`Canonical Correlation Analysis (CCA) <http://en.wikipedia.org/wiki/Canonical_correlation>`_,
and Minimum Energy Combination (MCE).

The third component of a BCI is an application to use the decoded data once it is received by the computer.
It needs to be useful to the person that is using the BCI, and it also needs to be simple enough that
the user can maintain control over this un-conventional task.
Our goal is to aid individuals with motor impairment, so our applications (apps) focus on ways to make the lives of these individuals
better.
Examples of our apps are a grid of phrases which can be navigated to select a specific phrase,
a TV remote control which interface with an IR transceiver to use a television, and a control interface
for a Mobile Robotic Platform for remote accessibility and interaction.