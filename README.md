# periodic-orbit-interface2D

This application uses TKinter python module to create an interface. On this interface, the user can place focal points in a 2D phase space and observe the resulting limit cycle, should there be one. The app models only the behaviour expected in the case of a 2D piecewise affine system. The system should present only two threshold values for domain definitions, one for each component. This then divides the 2D space in 4 different domains. They will be named as follow : $1$ (top-right), $2$ (top-left), $3$ (bottom-left) and $4$ (bottom-right). The trajectory will alternate domains in the following order : $1 \to 2 \to 3 \to 4 \to 1$. Two versions of the application are available, one with equal degradation rates called Visualisation_app_straight and the other with degradation rates depending on the component and the domain called Visualisation_app_non_straight.

## Precise mathematical context of the application use

## Application functionalities

The application presents different functionalities to customise your system and visualise the resulting behaviour. The application is mainly divided in four parts : the canvas, the tools panel, the entries panel and the results panel. The canvas is the interactive 2D space used to visualise your system behaviour. The tools panel is composed of different buttons allowing the user to either interact with the canvas, save the actual system setup or load other setups. The entries panel are used to enter precise parameter values. Finally, the result panel displays different computed properties of the system.

### Canvas panel

The canvas panel is the very core of this application. It consists of the a 2D interactive space with a Cartesian coordinate system. This 2D space is divided in four domains by two thresholds (one horizontal and one vertical). Different colors are used to denote each domain.

To start visualising trajectories, simply place a focal point in each of the four domains. To add a focal point, left-click on the canvas in the domain you wish to add the focal point. You'll notice that its color is the same as a domain one's, but with shifted of a quadrant. In fact, each focal point has the color of the domain \textbf{from which it is the focal point}. For example, a trajectory in starting in the purple domain (domain 1, top-right) will go toward the purple focal point until it switches to the yellow domain (domain 2, top-left).

As you've added the four focal points, you should now add the initial point of your trajectory. You can do so by right-clicking anywhere on the canvas (except at the intersection of the thresholds).

### Tools panel

### Entries panels

### Results panel

### Differences between the arbitrary and equal degradation coefficients versions
