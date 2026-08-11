# Spatial Modeling Cookbook

Record coordinate reference system, spatial unit, aggregation, boundary, resolution and time. Never use ordinary random CV when nearby observations leak information.

| Method | Use | Do not use | Assumptions/formulation | Validation/alternative |
|---|---|---|---|---|
| GIS overlay | geometry-based exposure/access | topology/CRS uncertain | spatial joins/buffers/network distance | spot-check geometry; raster/vector alternative |
| Moran's I/LISA | detect global/local autocorrelation | multiple local tests ignored | weighted spatial covariance | permutation test/FDR; variogram |
| Spatial regression | residual dependence/spillover | OLS causal claim | lag/error/Durbin structures | residual Moran, alternative W matrices |
| GWR/MGWR | exploratory spatially varying association | causal interpretation/small local sample | kernel-weighted local coefficients | spatial CV, bandwidth/collinearity; global model |
| Kriging | interpolation with spatial covariance | nonstationarity/poor variogram | covariance/variogram field model | blocked CV, variogram sensitivity; IDW/GP |

Test multiple spatial weight matrices, buffer/bandwidth choices, boundary changes and aggregation scales. Present uncertainty maps with legends and data coverage; never hide sparse regions. Ecological associations do not imply individual effects.

