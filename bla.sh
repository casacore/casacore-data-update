curl -H "X-GPG-PASSPHRASE: ${GPG_PASSPHRASE}" \
    -T casacore-data_20160111-1trusty_all.deb \
    -ugijzelaerr:${PASSWORD}  \
    "https://api.bintray.com/content/radio-astro/main/casacore-data/weekly/casacore-data_20160111-1trusty_all.deb;deb_distribution=stable;deb_component=main;deb_architecture=amd64;publish=1"
