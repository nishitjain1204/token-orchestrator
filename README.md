# Token Orchestrator
- Server capable of generating, assigning, and managing API keys with specific functionalities. 
- An endpoint to create new keys. Each generated key has a life of 5 minutes after which it gets deleted automatically if keep-alive operation is not run for that key (More details mentioned below).
- An endpoint to retrieve an available key, ensuring the key is randomly selected and not currently in use. This key should then be blocked from being served again until its status changes. If no keys are available, a 404 error should be returned.
- An endpoint to unblock a previously assigned key, making it available for reuse.
- An endpoint to permanently remove a key from the system.
- An endpoint for key keep-alive functionality, requiring clients to signal every 5 minutes to prevent the key from being deleted.
- Automatically release blocked keys within 60 seconds if not unblocked explicitly.
