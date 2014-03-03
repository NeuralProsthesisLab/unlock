#Unlock

<a href="http://d3js.org"><img src="http://d3js.org/logo.svg" align="left" hspace="10" vspace="6"></a>

Our goal is to develop BCI technology to help individuals suffering from locked-in syndrome [1] communicate.
Locked-in syndrome is characterized by an almost complete inability to communicate.  With current technology,
unfortunately, we cannot achieve this goal.

We think if more smart people are able to collaborate, then we have a better shot at accomplishing this goal.
Therefore, our strategy is to focus on providing a programming framework that makes it easier for researchers and
engineers to build BCI-based systems.  To this end, we employ a few simple ideas.

We encapsulate as much as possible, which is to say that we separate concerns.  We'll talk more about this later, but
the basic idea is that you should not need to know every corner of Unlock to create a new decoding algorithm or add a
language model or add a new acquisition device.

These could be different people with different skill sets, and we want them to be able to dive into their area and be
productive quickly.  One of the challenges with BCI technology is that it is inherently cross-disciplinary; therefore,
we want to lessen this burden as much as possible.

To support this goal, we need great documentation.  The documentation needs to be encapsulated too.  You should be able
to get a high-level idea of how the whole system works and also locate details about your specific area of interest
without arduous effort.

Finally, automate whenever possible; extra batteries included.  We want researchers and engineers to be able to get
going quickly.  Learning about all the dependencies and taking a bunch of manual steps can be overwhelming.  Especially
if someone just wants to hack out a quick idea.

In summary, the goal is to give you a great platform to hack out an idea.

The rest of this document is structured as follows.  %In the next section we provide a bit of history.
First we do a quick technical introduction.  After that, we discuss how to install and use Unlock, from a user
perspective.  Next, we cover both some of the internals from a high-level.  Finally we close with a example.

Development of the Unlock framework is funded by the Adaptive Brain-Computer Interactions (ABCI) Capstone
Project~\cite{abci}.

# Technical Introduction

The infrastructure Unlock provides can be logically separated into two distinct layers: the application layer and the
BCI layer.  These layers can in turn be further decomposed.

The BCI layer is defined by the signal-processing chain.  The signal-processing chain includes signal acquisition and
reconstruction, feature extraction and decoding, and command generation~\cite{neuraleng}.  Many BCI systems also
include a stimulation component, which is actually processed at the application layer; however, logically, the
stimulation component is part of the BCI.

For example, a paradigm based on Visually Evoked Potentials (VEP), flashes a graphical sequence at the user, which is
subsequently interpreted in the signal-processing chain~\cite{vep}.  But the actual flashing is handled at the
application layer.

We'll talk in more detail about the BCI layer in Section~\ref{bcisec}, but for now there is one important take away.
At each point in the pipeline we just discussed, the system is designed so that you can easily manipulate the data as
it flows through the system.

The application layer is model-view-controller (MVC)~\ref{mvc, mvc1} inspired.  Don't worry too much if you're not
familiar with MVC.  It's just a logical framework for structuring graphical user interfaces (GUIs).

The basic idea is that each application consists of three types of objects: models, views and controllers.  The
controllers accept user input (in this case BCI commands) and pass the inputs to the correct models.  Models handle
state transformation (the business logic if you will).  Finally, views observe the state objects(models) and render
themselves based on the current state of the world.

If you think about it, this also creates a pipeline in the application layer.  The take away here is that these
components are also encapsulated under interfaces.

Figure~\ref{unlock-components-fig} depicts the main components of Unlock.

Want to learn more? [See the docs.](https://github.com/NeuralProsthesisLab/unlock/blob/master/unlock/doc/unlock.pdf)

References
------------

[1] -   CELEST Capstone Project 1: [Adaptive Brain-Computer Interactions](http://celest.bu.edu/about-us/capstone-projects/adaptive-brain-computer-interactions.)

[2] -   Bauer, G. and Gerstenbrand, F. and Rumpl, E. Varieties of the locked-in syndrome. Journal
        of Neurology.  1979.