# VisualPing
A real time ping statistics visualization tool for any reachable server on the Internet.

This application is made out of two windows. The first one is intended to get the target
server on the Internet whose ping metrics are going to be visualized on real time. This
specification can be done either with a domain name (e.g. www.facebook.com) or with an
IP address (e.g. 192.168.0.162, useful if you want to troubleshoot networking issues on 
your private LAN). Once the target has been specified, the app pushes the second window,
which is the one intended to show real time ping statistics. These statistics are plotted
in two graphs: a local one and a global one. The local one shows the evolution of the
ping (round-trip-time) between the server and the client during the last 100 observations
(thus, the axis are changing linearly through time). This graph plots the average between
the last 5 ping values (slim line) and the log-error between the actual value and the 
windowed average, making it much easier to understand the graph since noisy observations
are filtered out. Finally, the global graph shows a colourized interpolation of the scatter 
plot of all the ping observations, indicating the mean and the percentiles nº 5 and 95.

### Demo
![](./visual_ping.gif)
