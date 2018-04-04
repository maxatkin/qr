from copy import deepcopy
import inspect
from IPython.display import display, HTML



HEADER = \
"""
<style>
.accordion {
    background-color: #eee;
    color: #444;
    cursor: auto;
    padding: 3px;
    width: 100%;
    text-align: left;
    border: none;
    outline: none;
    transition: 0.4s;
    font-size: 10px;    
}

.active, .accordion:hover {
    background-color: #ccc;
}

.panel {
    padding: 0 18px;
    background-color: white;
    display: block;
    overflow: visible;
    font-size: 10px;        
}
</style>
"""

SECTION = \
"""
<button class="accordion">{title}</button>
<div class="panel">
  <p>{content}</p>
</div>
"""


class Capture(object):
    def __init__(self, value, captures = None, func = None, source = None, func_call = None):
        self.value = value
        self.captures = captures if captures else []
        self.func = func if func else "input"
        self.source = source
        self.func_call = func_call if func_call else {}
        
    def printf(self, indent = 0):
        def get_value(a):
            if isinstance(a, Capture):
                return a.value
            else:
                return a 
        print ('\t' * indent) + str(self.func) + " :",
        if self.func != "input":
            print str({k: str(get_value(c)) for k, c in self.func_call.items()})
        print ('\t' * indent) + str(self.value)
        for c in self.captures:
            c.printf(indent + 1)
            
    def print_inputs(self, indent = 0):
        def get_value(a):
            if isinstance(a, Capture):
                return a.value
            else:
                return a         
        args = {k: get_value(c) for k, c in self.func_call.items() if not isinstance(c, Capture)}
        if len(args):
            print str(self.func)
            for k, v in args.items():
                print '\t %s:' % k,
                try:
                    display(HTML(v._repr_html_()))
                except:
                    print str(v)
                
        for c in self.captures:
            c.print_inputs(indent)
            
    def render_inputs(self, html_out = None, top = True):
        def get_value(a):
            if isinstance(a, Capture):
                return a.value
            else:
                return a
        def get_html(v):
            try:
                return v._repr_html_()
            except:
                return str(v)

        args = {k: get_value(c) for k, c in self.func_call.items() if not isinstance(c, Capture)}
        if len(args):
            title = self.func
            if html_out is None:
                html_out = HEADER
            disp = {str(k): get_html(v) for k, v in args.items()}
            content = ""
            for k, v in disp.items():
                content += "{}: {}<br>".format(k, v)

            html_out += SECTION.format(title = title, content = content)            
            
        for c in self.captures:
            html_out = c.render_inputs(html_out, top = False)             
        if top:
            return HTML(html_out)
        else:
            return html_out

    def _repr_html_(self):
        try:
            return self.value._repr_html_()
        except:
            return str(self.value)
        
def log_mode(mode = None):
    def log_imp(func):
        def decorator(*args, **kwargs):
            captures = []
            def get_value(a):
                if isinstance(a, Capture):
                    captures.append(deepcopy(a))
                    return a.value
                else:
                    captures.append(Capture(deepcopy(a)))
                    return a   
            actual_args = [get_value(a) for a in args]
            actual_kwargs = {k: get_value(v) for k, v in kwargs.items()}
            ret = func(*actual_args, **actual_kwargs)
            if mode == 'end':
                return ret
            else:
                return Capture(ret, captures, func.__name__, inspect.getsource(func), inspect.getcallargs(func, *args, **kwargs))
        return decorator
    return log_imp

log = log_mode()
endlog = log_mode('end')