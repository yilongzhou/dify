'use client'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useContext } from 'use-context-selector'
import cn from 'classnames'
import s from './index.module.css'
import type { File as FileEntity } from '@/models/datasets'
import { ToastContext } from '@/app/components/base/toast'

import { upload } from '@/service/base'

type IFileUploaderProps = {
  files: FileEntity[]
  onFileUpdate: (file?: FileEntity) => void
  onPreview: (file: FileEntity) => void
}

const ACCEPTS = [
  '.pdf',
  '.html',
  '.htm',
  '.md',
  '.markdown',
  '.txt',
  // '.xls',
  '.xlsx',
  '.csv',
]

const MAX_SIZE = 10 * 1024 * 1024

const FileUploader = ({ files, onFileUpdate, onPreview }: IFileUploaderProps) => {
  const { t } = useTranslation()
  const { notify } = useContext(ToastContext)
  const [dragging, setDragging] = useState(false)
  const dropRef = useRef<HTMLDivElement>(null)
  const dragRef = useRef<HTMLDivElement>(null)
  const fileUploader = useRef<HTMLInputElement>(null)
  const uploadPromise = useRef<any>(null)
  const [currentFile, setCurrentFile] = useState<File>()
  const [uploading, setUploading] = useState(false)
  const [percent, setPercent] = useState(0)

  // utils
  const getFileType = (currentFile: File) => {
    if (!currentFile)
      return ''

    const arr = currentFile.name.split('.')
    return arr[arr.length - 1]
  }
  const getFileSize = (size: number) => {
    if (size / 1024 < 10)
      return `${(size / 1024).toFixed(2)}KB`

    return `${(size / 1024 / 1024).toFixed(2)}MB`
  }

  const isValid = (file: File) => {
    const { size } = file
    const ext = `.${getFileType(file)}`
    const isValidType = ACCEPTS.includes(ext)
    if (!isValidType)
      notify({ type: 'error', message: t('datasetCreation.stepOne.uploader.validation.typeError') })

    const isValidSize = size <= MAX_SIZE
    if (!isValidSize)
      notify({ type: 'error', message: t('datasetCreation.stepOne.uploader.validation.size') })

    return isValidType && isValidSize
  }
  const onProgress = useCallback((e: ProgressEvent) => {
    if (e.lengthComputable) {
      const percent = Math.floor(e.loaded / e.total * 100)
      setPercent(percent)
    }
  }, [setPercent])
  const abort = () => {
    const currentXHR = uploadPromise.current
    currentXHR.abort()
  }
  // TODO
  const fileUpload = async (file?: File) => {
    if (!file)
      return

    if (!isValid(file))
      return

    setCurrentFile(file)
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    // store for abort
    const currentXHR = new XMLHttpRequest()
    uploadPromise.current = currentXHR
    try {
      const result = await upload({
        xhr: currentXHR,
        data: formData,
        onprogress: onProgress,
      }) as FileEntity
      onFileUpdate(result)
      setUploading(false)
    }
    catch (xhr: any) {
      setUploading(false)
      // abort handle
      if (xhr.readyState === 0 && xhr.status === 0) {
        if (fileUploader.current)
          fileUploader.current.value = ''

        setCurrentFile(undefined)
        return
      }
      notify({ type: 'error', message: t('datasetCreation.stepOne.uploader.failed') })
    }
  }
  const handleDragEnter = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    e.target !== dragRef.current && setDragging(true)
  }
  const handleDragOver = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }
  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    e.target === dragRef.current && setDragging(false)
  }
  // TODO
  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragging(false)
    if (!e.dataTransfer)
      return

    const files = [...e.dataTransfer.files]
    if (files.length > 1) {
      notify({ type: 'error', message: t('datasetCreation.stepOne.uploader.validation.count') })
      return
    }
    onFileUpdate()
    fileUpload(files[0])
  }

  const selectHandle = () => {
    if (fileUploader.current)
      fileUploader.current.click()
  }
  // TODO
  const removeFile = () => {
    if (fileUploader.current)
      fileUploader.current.value = ''

    setCurrentFile(undefined)
    onFileUpdate()
  }
  // TODO
  const fileChangeHandle = (e: React.ChangeEvent<HTMLInputElement>) => {
    const currentFile = e.target.files?.[0]
    onFileUpdate()
    fileUpload(currentFile)
  }

  useEffect(() => {
    dropRef.current?.addEventListener('dragenter', handleDragEnter)
    dropRef.current?.addEventListener('dragover', handleDragOver)
    dropRef.current?.addEventListener('dragleave', handleDragLeave)
    dropRef.current?.addEventListener('drop', handleDrop)
    return () => {
      dropRef.current?.removeEventListener('dragenter', handleDragEnter)
      dropRef.current?.removeEventListener('dragover', handleDragOver)
      dropRef.current?.removeEventListener('dragleave', handleDragLeave)
      dropRef.current?.removeEventListener('drop', handleDrop)
    }
  }, [])

  return (
    <div className={s.fileUploader}>
      <input
        ref={fileUploader}
        id="fileUploader"
        style={{ display: 'none' }}
        type="file"
        multiple
        accept={ACCEPTS.join(',')}
        onChange={fileChangeHandle}
      />
      <div className={s.title}>{t('datasetCreation.stepOne.uploader.title')}</div>
      <div ref={dropRef} className={cn(s.uploader, dragging && s.dragging)}>
        <div className='flex justify-center items-center h-6 mb-2'>
          <span className={s.uploadIcon}/>
          <span>{t('datasetCreation.stepOne.uploader.button')}</span>
          <label className={s.browse} onClick={selectHandle}>{t('datasetCreation.stepOne.uploader.browse')}</label>
        </div>
        <div className={s.tip}>{t('datasetCreation.stepOne.uploader.tip')}</div>
        {dragging && <div ref={dragRef} className={s.draggingCover}/>}
      </div>
      <div className={s.fileList}>
        {currentFile && (
          <div
            // onClick={() => onPreview(currentFile)}
            className={cn(
              s.file,
              uploading && s.uploading,
              // s.active,
            )}
          >
            {uploading && (
              <div className={s.progressbar} style={{ width: `${percent}%` }}/>
            )}
            <div className={s.fileInfo}>
              <div className={cn(s.fileIcon, s[getFileType(currentFile)])}/>
              <div className={s.filename}>{currentFile.name}</div>
              <div className={s.size}>{getFileSize(currentFile.size)}</div>
            </div>
            <div className={s.actionWrapper}>
              {uploading && (
                <div className={s.percent}>{`${percent}%`}</div>
              )}
              {!uploading && (
                <div className={s.remove} onClick={removeFile}/>
              )}
            </div>
          </div>
        )}
      </div>
      {/* TODO */}
      {!currentFile && files[0] && (
        <div
          // onClick={() => onPreview(currentFile)}
          className={cn(
            s.file,
            uploading && s.uploading,
            s.active,
          )}
        >
          {uploading && (
            <div className={s.progressbar} style={{ width: `${percent}%` }}/>
          )}
          <div className={s.fileInfo}>
            <div className={cn(s.fileIcon, s[getFileType(files[0])])}/>
            <div className={s.filename}>{files[0].name}</div>
            <div className={s.size}>{getFileSize(files[0].size)}</div>
          </div>
          <div className={s.actionWrapper}>
            {uploading && (
              <div className={s.percent}>{`${percent}%`}</div>
            )}
            {!uploading && (
              <div className={s.remove} onClick={removeFile}/>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default FileUploader
