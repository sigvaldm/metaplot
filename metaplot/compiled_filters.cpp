#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>

namespace py = pybind11;

void ema(py::array_t<double> t, py::array_t<double> x, double tau){

    py::buffer_info xinfo = x.request();
    py::buffer_info tinfo = t.request();

    auto x_ = static_cast<double *>(xinfo.ptr);
    auto t_ = static_cast<double *>(tinfo.ptr);

    auto size = xinfo.shape[0];
    for(py::ssize_t i=1; i<size; i++){
        double w = std::exp(-(t_[i]-t_[i-1])/tau);
        x_[i] = (1-w)*x_[i] + w*x_[i-1];
    }
}

PYBIND11_MODULE(compiled_filters, m){
    m.doc() = "pybind11 example plugin";
    m.def("ema", &ema, "Exponential Moving Average");
}
