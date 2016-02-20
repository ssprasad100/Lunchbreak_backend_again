innodb_buffer_pool_size: 100M

branches:
  development:
    path: /vagrant/lunchbreak
    host: local.lunchbreakapp.be
    ssl: False
    certificates:
      business: business_development.pem
      customers: customers_development.pem
    branch: development
    requirements: dev-requirements.txt