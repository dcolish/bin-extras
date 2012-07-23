import Control.Applicative
import Control.Monad
import Data.Maybe
import Data.Text
import Prelude hiding (break, drop)
import System.Environment

main = drop 1 . snd . break (== ':') . pack <$> getEnv "PATH"


