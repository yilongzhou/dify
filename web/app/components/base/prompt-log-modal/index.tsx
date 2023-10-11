import type { FC } from 'react'
import Card from './card'
import CopyFeedback from '@/app/components/base/copy-feedback'
import { XClose } from '@/app/components/base/icons/src/vender/line/general'

type PromptLogModalProps = {
  width: number
}
const PromptLogModal: FC<PromptLogModalProps> = ({
  width,
}) => {
  return (
    <div
      className='fixed top-16 left-2 bottom-2 bg-white border-[0.5px] border-gray-200 rounded-xl shadow-xl z-10'
      style={{ width }}>
      <div className='flex justify-between items-center pl-6 pr-5 h-14 border-b border-b-gray-100'>
        <div className='text-base font-semibold text-gray-900'>PROMPT LOG</div>
        <div className='flex items-center'>
          <CopyFeedback className='w-6 h-6' content='' selectorId='' />
          <div className='mx-2.5 w-[1px] h-[14px] bg-gray-200' />
          <div className='flex justify-center items-center w-6 h-6 cursor-pointer'>
            <XClose className='w-4 h-4 text-gray-500' />
          </div>
        </div>
      </div>
      <div className='p-2'>
        <Card />
      </div>
    </div>
  )
}

export default PromptLogModal