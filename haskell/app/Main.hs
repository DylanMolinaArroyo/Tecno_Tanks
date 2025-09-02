{-# LANGUAGE ImportQualifiedPost #-}

import Control.Concurrent (forkIO)
import Control.Monad (forever)
import Data.Aeson (FromJSON, decode, parseJSON, withObject, (.:))
import Data.Aeson.Key (fromString)
import Data.ByteString.Lazy qualified as BL
import Data.Map qualified as Map
import Data.Maybe (fromMaybe)
import Data.PSQueue (PSQ)
import Data.PSQueue qualified as PSQ
import Data.Text (pack)
import Data.Text.Encoding (encodeUtf8)
import Network.Socket
import System.IO

-- Structure for receiving data
data InputData = InputData
  { coordenadaJugador :: (Int, Int),
    coordenadaEnemigo :: (Int, Int),
    matrix :: [[String]]
  }
  deriving (Show)

instance FromJSON InputData where
  parseJSON = withObject "InputData" $ \v -> do
    jugador <- v .: fromString "coordenadaJugador"
    enemigo <- v .: fromString "coordenadaEnemigo"
    matrix <- v .: fromString "matrix"
    return InputData {coordenadaJugador = jugador, coordenadaEnemigo = enemigo, matrix = matrix}

adjacentCoords :: (Int, Int) -> [(Int, Int)]
adjacentCoords (x, y) = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

manhattanDistance :: (Int, Int) -> (Int, Int) -> Int
manhattanDistance (x1, y1) (x2, y2) = abs (x1 - x2) + abs (y1 - y2)

-- Algorithming A*
aStar :: (Int, Int) -> (Int, Int) -> [[String]] -> Handle -> IO ()
aStar jugador enemigo matriz handle = do
  let openSet = PSQ.singleton jugador (manhattanDistance jugador enemigo)
      cameFrom = Map.empty
      gScore = Map.singleton jugador 0
      fScore = Map.singleton jugador (manhattanDistance jugador enemigo)
  astarHelper openSet cameFrom gScore fScore enemigo matriz handle

astarHelper :: PSQ (Int, Int) Int -> Map.Map (Int, Int) (Int, Int) -> Map.Map (Int, Int) Int -> Map.Map (Int, Int) Int -> (Int, Int) -> [[String]] -> Handle -> IO ()
astarHelper openSet cameFrom gScore fScore objetivo matriz handle
  | PSQ.null openSet = putStrLn "Couldn't find route."
  | current == objetivo = do
      let ruta = reconstruirRuta cameFrom current
      putStrLn "Route found:"
      print ruta
      enviarRutaARemote ruta handle -- Send route to client
  | otherwise = do
      let openSet' = PSQ.deleteMin openSet
          vecinos = filter (esTransitable matriz) (adjacentCoords current)
      let (newOpenSet, newCameFrom, newGScore, newFScore) = foldl (procesarVecino current objetivo gScore fScore) (openSet', cameFrom, gScore, fScore) vecinos
      astarHelper newOpenSet newCameFrom newGScore newFScore objetivo matriz handle
  where
    current = PSQ.key (fromMaybe (error "Error con PSQ") (PSQ.findMin openSet))

-- Checks if a coordentae its transitable
esTransitable :: [[String]] -> (Int, Int) -> Bool
esTransitable matriz (x, y) =
  let valor = (matriz !! y) !! x
   in valor == "3" || valor == "-1"

-- Procces neighbor
procesarVecino :: (Int, Int) -> (Int, Int) -> Map.Map (Int, Int) Int -> Map.Map (Int, Int) Int -> (PSQ (Int, Int) Int, Map.Map (Int, Int) (Int, Int), Map.Map (Int, Int) Int, Map.Map (Int, Int) Int) -> (Int, Int) -> (PSQ (Int, Int) Int, Map.Map (Int, Int) (Int, Int), Map.Map (Int, Int) Int, Map.Map (Int, Int) Int)
procesarVecino current objetivo _ _ (openSet, cameFrom, gScore', fScore') vecino =
  let tentativeGScore = fromMaybe (maxBound :: Int) (Map.lookup current gScore') + 1
   in if tentativeGScore < fromMaybe (maxBound :: Int) (Map.lookup vecino gScore')
        then
          let newCameFrom = Map.insert vecino current cameFrom
              newGScore = Map.insert vecino tentativeGScore gScore'
              newFScore = Map.insert vecino (tentativeGScore + manhattanDistance vecino objetivo) fScore'
              newOpenSet = PSQ.insert vecino (tentativeGScore + manhattanDistance vecino objetivo) openSet
           in (newOpenSet, newCameFrom, newGScore, newFScore)
        else (openSet, cameFrom, gScore', fScore')

reconstruirRuta :: Map.Map (Int, Int) (Int, Int) -> (Int, Int) -> [(Int, Int)]
reconstruirRuta cameFrom current
  | Map.member current cameFrom = current : reconstruirRuta cameFrom (fromMaybe (0, 0) (Map.lookup current cameFrom))
  | otherwise = [current]

-- Function to send tha route back to the client
enviarRutaARemote :: [(Int, Int)] -> Handle -> IO ()
enviarRutaARemote ruta handle = do
  let rutaFormato = map (\(x, y) -> [x, y]) ruta
  let rutaTexto = show rutaFormato
  hPutStrLn handle rutaTexto

handleClient :: Handle -> IO ()
handleClient handle = do
  dataLine <- hGetLine handle
  putStrLn "Connection established for Python client"

  -- Decode JSON
  let maybeData = decode (BL.fromStrict (encodeUtf8 (pack dataLine))) :: Maybe InputData
  case maybeData of
    Just inputData -> do
      aStar (coordenadaJugador inputData) (coordenadaEnemigo inputData) (matrix inputData) handle
      handleClient handle
    Nothing -> putStrLn "Error: Couldn't decode pachage received."

main :: IO ()
main = withSocketsDo $ do
  addrinfos <- getAddrInfo (Just (defaultHints {addrFlags = [AI_PASSIVE]})) Nothing (Just "3000")
  let serveraddr = head addrinfos

  sock <- socket (addrFamily serveraddr) Stream defaultProtocol
  bind sock (addrAddress serveraddr)
  listen sock 1

  putStrLn "Haskell waiting for connections..."

  forever $ do
    (conn, _) <- accept sock
    handle <- socketToHandle conn ReadWriteMode
    hSetBuffering handle LineBuffering

    putStrLn "Connection established with client."

    _ <- forkIO $ handleClient handle

    return ()