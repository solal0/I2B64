# I2B64
I2B64 (Image to Base64) is a tool who uses python, RLE and Base64 to turn Images into Base64.

Then, using Roblox's editable images decodes the Base64 into an actual roblox image.

# How to use

Download I2B64.py and I2B64.luau from the latest release

## Compile using Python

1. Run I2B64.py and select Compile action
2. Select your image file
3. Save your image's data file

## Decompile in Roblox
1. Copy the content of the image's data file
2. Paste it in a roblox ModuleScript
3. Copy the content of I2B64.luau
4. Paste it in a roblox ModuleScript
5. Finally, you can use I2B64's base64toImage function like so:

```luau
local I2B64 = require(game.ReplicatedStorage.I2B64) -- I2B64.luau
local data = require(game.ReplicatedStorage.ImageData) -- your image's data file content / return [[ base64 ]]

local image, raw, X, Y = I2B64.base64toImage(data) -- the one and only function

-- gui creation to display the image
local gui = Instance.new("ScreenGui",game.Players.LocalPlayer.PlayerGui)
local img = Instance.new("ImageLabel",gui)
img.Size = UDim2.fromOffset(X, Y)
img.ImageContent = image
```
