{-# LANGUAGE NamedFieldPuns #-}
module Context01 where
import System.IO (hPutStr, stderr, stdout, hFlush)
import System.Environment
import qualified Values
import Control.Monad.Trans.Class
import Control.Exception
import EvaluationUtils
import qualified Submission
value_file = "RDOJEjCXb_values.txt"
exception_file = "RDOJEjCXb_exceptions.txt"
writeSeparator :: IO ()
writeSeparator = do
    hPutStr stderr "--RDOJEjCXb-- SEP"
    hPutStr stdout "--RDOJEjCXb-- SEP"
    appendFile value_file "--RDOJEjCXb-- SEP"
    appendFile exception_file "--RDOJEjCXb-- SEP"
    hFlush stdout
    hFlush stderr
sendValue :: Values.Typeable a => a -> IO ()
sendValue = Values.sendValue value_file
sendException :: Exception e => Maybe e -> IO ()
sendException = Values.sendException exception_file
sendSpecificValue :: EvaluationResult -> IO ()
sendSpecificValue = Values.sendEvaluated value_file
sendSpecificException :: EvaluationResult -> IO ()
sendSpecificException = Values.sendEvaluated exception_file
handleException :: Exception e => (Either e a) -> Maybe e
handleException (Left e) = Just e
handleException (Right _) = Nothing
main = do
    writeSeparator
    let mainArgs = {}
    result <- try (withArgs mainArgs Submission.main) :: IO (Either SomeException ())
    let ee = handleException result in sendException (ee)
    putStr ""