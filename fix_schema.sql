
ALTER TABLE service_requests_servicerequest DROP COLUMN IF EXISTS email_count;
ALTER TABLE service_requests_servicerequest DROP COLUMN IF EXISTS email_sent;
ALTER TABLE service_requests_servicerequest DROP COLUMN IF EXISTS last_email_sent_at;
ALTER TABLE service_requests_servicerequest DROP COLUMN IF EXISTS title;
ALTER TABLE service_requests_servicerequest DROP COLUMN IF EXISTS priority;
ALTER TABLE service_requests_servicerequest DROP COLUMN IF EXISTS resolution;