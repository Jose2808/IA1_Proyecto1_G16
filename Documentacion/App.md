# Proyecto - Grupo 16

## INTEGRANTES

|   Carne   |        Nombre Completo        |
| :-------: | :---------------------------: |
| 202010055 |      Derek Esquivel Díaz      |
| 202004804 | José Andrés Montenegro Santos |

## Objetivos de ña documentacion

- Dar a entender la arquitectura que se utilizó para crear la aplicación, a manera de brindar una idea a las personas acerca de la forma en la que funciona y las tecnologías que se utilizaron.


- Explicar de una forma clara la configuración de cada uno de las librarias  utilizadas en el proyecto, a manera de dar una idea de cual es el propósito de cada una.


## Documentación
Este proyecto consiste en una aplicacion para android que reconoce dinosaurios utilizando la camara del dispositivo. El reconocimiento se realiza mediante un modelo de machine learning TensorFlow Lite entrenado previamente.

### Permisos
Al inicio de nuestra MainActivity, se deberá de obtener los permisos de la aplicación. En este caso se utilizará la camara trasera del dispositivo, por lo que es necesario obtener permiso para utilizarla. Primero definiremos un código de respuesta para la solicitud de servicios y un Array con los permisos.
```kotlin
// Constants
private const val REQUEST_CODE_PERMISSIONS = 999 // Return code after asking for permission
private val REQUIRED_PERMISSIONS = arrayOf(Manifest.permission.CAMERA) // permission needed
```

Luego al montar la aplicación se comprobará si ya se poseen los permisos para utilizar la cámara.

```kotlin
if (allPermissionsGranted()) {
    startCamera()
} else {
    ActivityCompat.requestPermissions(
        this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS
    )
}
```
Esta validación se realizará con la funcion ```checkSelfPermission``` incluida en el SDK para comprobar si los permisos ya fueron otorgados (como seria en el caso de que no es la primera vez que se ejecuta).

```kotlin
private fun allPermissionsGranted(): Boolean = REQUIRED_PERMISSIONS.all {
    ContextCompat.checkSelfPermission(
        baseContext, it
    ) == PackageManager.PERMISSION_GRANTED
}
```

Sí ya se poseen los servicios se procede a inicializar la camara, si no se realiza la solicitud.

En la aplicación se ha sobreescrito la funcion para poder controlar la respuesta que se da luego de la solicitud de los permisos, esto permitirá mostrar un mensaje al usuario informandole que los permisos no fueron otorgados y cerrará la aplicación.

```kotlin
override fun onRequestPermissionsResult(
    requestCode: Int,
    permissions: Array<String>,
    grantResults: IntArray
) {
    if (requestCode == REQUEST_CODE_PERMISSIONS) {
        if (allPermissionsGranted()) {
            startCamera()
        } else {
            Toast.makeText(
                this,
                getString(R.string.permission_deny_text),
                Toast.LENGTH_SHORT
            ).show()
            finish()
        }
    }
}
```

### Inicializar la cámara
Esta aplicación utilizá la camara para reconocer imagenes en tiempo real, por lo tanto se debera de inicializar la cámara y configurarla para que tome fotografias constantemente que luego son alimentadas en el modelo de machine learning para ser reconocidas.

Al iniciar se creará instancia del proceso de la camara

```Kotlin
private fun startCamera() {
    val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
```

Luego deberemos de agregar a esta instancia un listener, que sera el encargado de tomar las fotografias y enviarlas para analizar

```Kotlin
    cameraProviderFuture.addListener(Runnable {
        val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()
```

Luego se iniciará el analizador de imagenes nativo de android, para esto se debera de seleccionar la resolucion de las fotogradias. Luego se especifica la estategia de las imagenes, en este caso tomara fotografias cada frame pero solo mantendra en memoria la ultima captura. Luego se agrega la intancia del modelo de TensorFlow (Se explicará mas adelante).

```Kotlin
        imageAnalyzer = ImageAnalysis.Builder()
            .setTargetResolution(Size(224, 224))
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
            .also { analysisUseCase: ImageAnalysis ->
                analysisUseCase.setAnalyzer(cameraExecutor, ImageAnalyzer(this) { items ->
                    recogViewModel.updateData(items)
                })
            }
```


Luego se selecciona la camara a utilizar, la aplicación usara la camara por defecto del dospositivo si esta disponible, si no utilizara la camara frontal.

Por ultimo se enlazará la camara al ciclo de vida de la aplicación y se mostrara un preview de la camara en pantalla


```Kotlin
        val cameraSelector =
            if (cameraProvider.hasCamera(CameraSelector.DEFAULT_BACK_CAMERA))
                CameraSelector.DEFAULT_BACK_CAMERA else CameraSelector.DEFAULT_FRONT_CAMERA

        try {
            cameraProvider.unbindAll()

            camera = cameraProvider.bindToLifecycle(
                this, cameraSelector, preview, imageAnalyzer
            )

            preview.setSurfaceProvider(viewFinder.surfaceProvider)
        } catch (exc: Exception) {
            Log.e(TAG, "Use case binding failed", exc)
        }

```

### Analizar Imagenes
Una vez se tienen las imagenes de la camara estas deberan de ser analizadas. Esto como se menciono anteriormente se realizara con un modelo TensorFlow Lite.

Lo primero que se hara será cargar el modelo:

```kotlin
    private class ImageAnalyzer(ctx: Context, private val listener: RecognitionListener) :
        ImageAnalysis.Analyzer {

            private val model = Dinosaurios3.newInstance(ctx)

        ...
        }

```

Una vez cargado el modelo escribimos la función para analizar la imagen:

```kotlin
override fun analyze(imageProxy: ImageProxy) {

    val items = mutableListOf<Recognition>()

    val tfImage = TensorImage(DataType.FLOAT32)
    tfImage.load(toBitmap(imageProxy))
    val outputs = model.process(tfImage)
    val probability = outputs.probabilityAsCategoryList

    if(probability[0].score > probability[1].score){
        items.add(Recognition(probability[0].label, probability[0].score))

    } else {
        items.add(Recognition(probability[1].label, probability[1].score))
    }

    listener(items.toList())


    imageProxy.close()
}
```
Lo que se hara en esta funcion es procesar la imagen recibida de la camara a un bitmap. este bitmap sera convertida en una imagen de tensorflow que podra ser procesada por el modelo.

El modelo regresará una lista con los objetos reconocidos, con su label y probabilidad. Se enviará el resultado mas grande al listener.

