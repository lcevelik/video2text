# FonixFlow Release Scripts

This directory contains scripts and templates for building and distributing FonixFlow releases.

## Files

- **build_release.sh** - Main release build script
- **manifest.json** - Template for the update server manifest

## Building a Release

### Prerequisites

1. Ensure you have all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your CDN/hosting for updates:
   - AWS S3 + CloudFront, or
   - GitHub Releases, or
   - Your own server

3. Configure the update server URL in `gui/update_manager.py`:
   ```python
   self.update_server = "https://cdn.fonixflow.com/updates"
   ```

### Build Steps

1. **Build the release:**
   ```bash
   ./scripts/build_release.sh 1.0.0
   ```

   This will:
   - Update `app/version.py` with the new version
   - Encode the license file (licenses.txt → licenses.dat)
   - Build the .app bundle with PyInstaller
   - Create a ZIP file: `dist/FonixFlow-1.0.0.zip`
   - Calculate SHA256 hash
   - Generate manifest file: `dist/FonixFlow-1.0.0-manifest.json`

2. **Test the build locally:**
   ```bash
   open dist/FonixFlow.app
   ```

   Verify:
   - App launches correctly
   - Version shows correctly in logs
   - License validation works
   - All features work as expected

3. **Upload to CDN:**
   ```bash
   # Example for AWS S3
   aws s3 cp dist/FonixFlow-1.0.0.zip s3://your-bucket/releases/

   # Make it publicly accessible
   aws s3api put-object-acl \
     --bucket your-bucket \
     --key releases/FonixFlow-1.0.0.zip \
     --acl public-read
   ```

4. **Update the manifest on your server:**

   Copy the contents from `dist/FonixFlow-1.0.0-manifest.json` and update your `manifest.json` file at:
   ```
   https://cdn.fonixflow.com/updates/manifest.json
   ```

   The manifest should contain:
   ```json
   {
     "latest_version": "1.0.0",
     "download_url": "https://cdn.fonixflow.com/releases/FonixFlow-1.0.0.zip",
     "release_notes": "Update description here",
     "force_update": false,
     "file_hash": "abc123...",
     "file_size": "125M",
     "minimum_version": "1.0.0",
     "published_at": "2024-12-01T12:00:00Z"
   }
   ```

5. **Test the update:**
   - Install an older version of FonixFlow
   - Launch it
   - Wait 3 seconds (auto-check delay)
   - Verify update dialog appears
   - Test the download and installation

## Release Checklist

Before releasing:

- [ ] All tests pass
- [ ] Version number updated
- [ ] Release notes written
- [ ] License file encoded
- [ ] Build succeeds
- [ ] Local testing completed
- [ ] ZIP file uploaded to CDN
- [ ] Manifest updated on server
- [ ] Update flow tested from previous version
- [ ] GitHub release created (optional)

## Version Numbering

FonixFlow uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR** - Breaking changes, major new features
- **MINOR** - New features, backwards compatible
- **PATCH** - Bug fixes, small improvements

Examples:
- `1.0.0` - Initial release
- `1.0.1` - Bug fix
- `1.1.0` - New feature (e.g., new transcription model)
- `2.0.0` - Major update (e.g., redesigned UI)

## Hosting Options

### Option 1: GitHub Releases (Recommended for small projects)

1. Create a GitHub release with tag `v1.0.0`
2. Upload the ZIP file as a release asset
3. Use the GitHub CDN URL in manifest:
   ```
   https://github.com/username/repo/releases/download/v1.0.0/FonixFlow-1.0.0.zip
   ```
4. Host `manifest.json` on GitHub Pages or a simple server

### Option 2: AWS S3 + CloudFront (Recommended for production)

1. Create S3 bucket for releases
2. Set up CloudFront distribution
3. Upload ZIP files to S3
4. Update manifest.json in S3
5. Use CloudFront URL in update_manager.py

### Option 3: Your Own Server

1. Set up HTTPS server
2. Create `/updates/` directory
3. Upload ZIP files
4. Host manifest.json at `/updates/manifest.json`
5. Ensure CORS is configured if needed

## Troubleshooting

### Build fails

- Check PyInstaller logs
- Verify all dependencies are installed
- Ensure ffmpeg is available

### Updates not detecting

- Check `update_manager.py` has correct server URL
- Verify manifest.json is accessible
- Check logs for update check errors
- Ensure 24-hour throttle hasn't blocked check

### Download fails

- Verify ZIP file is publicly accessible
- Check download_url in manifest
- Test URL directly in browser

### Installation fails

- Verify SHA256 hash matches
- Check app has write permissions to /Applications
- Review installation logs

## Support

For issues or questions, check the main project README or open an issue on GitHub.
