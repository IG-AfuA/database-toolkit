<?php
include 'ClassMarkerApiClient.php';

$categories = file('Classmarker_Kategorien_rename.txt');

$cm_client = new ClassMarkerClient($key, $secret);

foreach($categories as $category) {
    $category = preg_replace('/\R+/', '', $category);
    list($pk, $text) = explode(" ", $category, 2);
    print($pk." --> ".$text."\n");
    $json_response = $cm_client->updateParentCategory($pk, $text);
    echo $json_response;
    sleep(5);
}
?>
