<?php


    use Google\Cloud\Vision\VisionClient;


    // On chage composer
    require_once 'vendor/autoload.php';


    // On récupère l'image à scanner
    $file = $_FILES["image"];


    // On déplace l'image dans le dossier de traitement
    move_uploaded_file($file['tmp_name'], __DIR__ . "/export/image.jpg");


    // Utilisation de l'API Google Cloud Vision
    $vision = new VisionClient([
        'keyFilePath' => __DIR__ . "/keyFile.json",
    ]);

    // Lecture de l'image
    $image = $vision->image(
        fopen(__DIR__ . "/export/image.jpg", "r"),
        ['FACE_DETECTION'] // Ici nous voulons chercher des visages, mais il est possible de rechercher d'autres types
    );

    // Récupération des résultats
    $annotation = $vision->annotate($image);

    // On parcourt les visages trouvés
    // Et comme nous allons écrire sur l'image, nous devons en créer une nouvelle
    $output = imagecreatefromjpeg(__DIR__ . "/export/image.jpg");

    foreach ($annotation->faces() as $face) {
        $vertices = $face->boundingPoly()['vertices'];

        $x1 = $vertices[0]['x'];
        $y1 = $vertices[0]['y'];
        $x2 = $vertices[2]['x'];
        $y2 = $vertices[2]['y'];

        imagerectangle($output, $x1, $y1, $x2, $y2, 0x00ff00);
    }


    // Affichage de l'image à l'utilisateur
    header('Content-Type: image/jpeg');
    imagejpeg($output);
    imagedestroy($output);