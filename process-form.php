<?php
// This script will process the form data and send the email.

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Collect and sanitize the form data
    $name = htmlspecialchars(trim($_POST['name']));
    $email = htmlspecialchars(trim($_POST['email']));
    $service = htmlspecialchars(trim($_POST['service']));
    $message = htmlspecialchars(trim($_POST['message']));

    // The recipient email address
    // Make sure this is a working email address.
    $to = "dv3nt@duck.com";
    
    // The email subject line
    $subject = "New message from ANSCOM: " . $service;

    // The email content
    $email_content = "Name: $name\n";
    $email_content .= "Email: $email\n\n";
    $email_content .= "Service: $service\n\n";
    $email_content .= "Message:\n$message\n";

    // Build the email headers
    $email_headers = "From: $name <$email>";

    // Send the email
    if (mail($to, $subject, $email_content, $email_headers)) {
        // Redirect to the thank you page after successful email send
        header("Location: /templates/thank-you.html");
        exit;
    } else {
        // Optional: Handle a failed email send
        // You can redirect to an error page or show a message.
        // For now, it will simply do nothing on failure.
    }
}
?>
