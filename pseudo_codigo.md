# Valores

Hay ciertos UUID que identifican ciertas funcionalidades:
 - ServiceUUID = "DAB91435-B5A1-E29C-B041-BCD562613BE4"
 - SubscribeCharacteristic = "DAB91382-B5A1-E29C-B041-BCD562613BE4"
 - WriteCharacteristic = "DAB91383-B5A1-E29C-B041-BCD562613BE4"
 - RadioSubCharacteristic = "DAB90756-B5A1-E29C-B041-BCD562613BE4"
 - RadioWriteCharacteristic = "DAB90757-B5A1-E29C-B041-BCD562613BE4"


# Métodos

## DiscoverCharacteristics m__4

Comprueba si ya se habían asignados los ids y establece el boolean correspondiente si coincide el serviceUUID y el characteristicUUID. También llama a `SubscribeCharacteristics` si todavía no estaba suscripto (y establece a 1 _isSubscribed).

## SubscribeCharacteristics

 1. Llama a `SubscribeCharacteristics m__5` con ServiceUUID y SubscribeCharacteristic como argumentos y registra una acción con BluetoothLEHardwareInterface::SubscribeCharacteristicWithDeviceAddress.
 2. Llama a `SubscribeCharacteristics m__6` con ServiceUUID y RadioSubCharacteristic como argumentos y registra una acción con BluetoothLEHardwareInterface::SubscribeCharacteristicWithDeviceAddress.
 3. Llama a BLEManager::TagAnalyticForFirstConnection si está conectado.
 4. Obtiene la acción de BLEManager::BLEConnectionCompleteCallback y si existe la llama.
 5. Obtiene la acción de BLEManager::OnBLEStatusChanged y si existe la llama (con un true/1 como argumento).


## SubscribeCharacteristics m__5

Llama a BLEManager::DataRecieved(unsigned int8[])

## SubscribeCharacteristics m__6

Llama a BLEManager::RadioDataReceived(unsigned int8[])