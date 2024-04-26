<?php
include 'ClassMarkerApiClient.php';
include 'config.inc';

$categories = file('categories.txt');

$cm_client = new ClassMarkerClient($key, $secret);

foreach($categories as $category)
{
    # Strip newline
    $category = preg_replace('/\R+/', '', $category);
    echo $category."\n";
    $json_response = $cm_client->addParentCategory($category);
    echo $json_response;

    $json = json_decode($json_response);
    $json_response = $cm_client->addCategory($json->parent_category->parent_category_id, 'Klasse E');
    echo $json_response;
    $json_response = $cm_client->addCategory($json->parent_category->parent_category_id, 'Klasse A');
    echo $json_response;
}
?>
