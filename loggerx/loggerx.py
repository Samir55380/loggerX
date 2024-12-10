# loggerx/loggerx.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Callable

try:
    import graypy
except ImportError:
    graypy = None


class LoggerX:
    """
    LoggerX is a wrapper for the logging module that logs exceptions and stack traces.
    """

    def __init__(
        self,
        stackTrace: bool = False,
        path: str = "./log.log",
        name: str = "main-log",
        max_size_mb: int = 150,
        send_to_graylog: bool = False,
        graylog_host: str = "",
        port: int = 12201,
    ) -> None:
        """
        Any function wrapped with LoggerX will run inside a try-except block with Exception (see __call__).
        If you still need to handle the exception and still want a log, use the raise keyword.

        Args:
            stackTrace (bool, optional): Prints stackTrace into log.
            path (str, optional): Path to the log.
            name (str, optional): Name for the logger instance.
            max_size_mb (int, optional): Maximum log size in MB.
            send_to_graylog (bool, optional): Send logs to a Graylog server.
            graylog_host (str, optional): Hostname of the Graylog server.
            port (int, optional): Port of the Graylog server.
        """
        self.path = path
        self.name = name
        self.stackTrace = stackTrace
        self.max_size_mb = int(max_size_mb)
        self.send_to_graylog = send_to_graylog
        self.graylog_host = graylog_host
        self.port = port

        if self.send_to_graylog:
            if graypy is None:
                raise ImportError("graypy is not installed. Install it with `pip install graypy`.")
            self.set_graylog()
        else:
            self.setup_logging()

    def setup_logging(self) -> None:
        if not hasattr(self, "logger"):
            formatter = logging.Formatter("[%(asctime)s]-%(levelname)s-[%(process)d]-%(name)s: %(message)s ")
            self.logger = logging.getLogger(f"instance_name: {self.name}")
            self.logger.setLevel(logging.DEBUG)
            self.create_rotating_log(self.path, formatter)
            self.create_stream_stdout(formatter)

    def set_graylog(self) -> None:
        handler = graypy.GELFUDPHandler(self.graylog_host, self.port)
        formatter = logging.Formatter("[%(asctime)s]-%(levelname)s-[%(process)d]-%(name)s: %(message)s ")
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        self.create_rotating_log(self.path, formatter)
        self.create_stream_stdout(formatter)
        if not any(isinstance(h, graypy.GELFUDPHandler) for h in self.logger.handlers):
            self.logger.addHandler(handler)

    def create_rotating_log(self, path: str, formatter: logging.Formatter) -> None:
        """
        Creates a rotating log
        """
        maxMB = int(self.max_size_mb)  # maximum log size in MB
        handler = RotatingFileHandler(path, maxBytes=maxMB * 1024 * 1024, backupCount=5)
        handler.setFormatter(formatter)
        if not any(isinstance(h, RotatingFileHandler) for h in self.logger.handlers):
            self.logger.addHandler(handler)

    def create_stream_stdout(self, formatter: logging.Formatter) -> None:
        """Add log stream to stdout

        Args:
            formatter (logging.Formatter): Formatter object
        """
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            self.logger.addHandler(handler)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        @Decorator
        that wraps a function and if an exception happens, it will log it.
        """

        def wrapper(*args: Any, **kwargs: Any) -> Any:  # Adjust the return type here
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                self.logger.error("[ERROR]: %s", str(ex), exc_info=self.stackTrace)

        return wrapper
