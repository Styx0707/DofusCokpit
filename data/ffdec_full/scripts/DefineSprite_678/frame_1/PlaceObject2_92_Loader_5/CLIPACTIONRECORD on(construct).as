on(construct){
   while(true)
   {
      if(!(0x26003237 & 0x26003237))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x03");
      }
      if(ord(§§pop()))
      {
         if(false)
         {
            setProperty(§§pop(), _X, §§pop());
         }
         autoLoad = true;
         centerContent = false;
         contentPath = "";
         enabled = false;
         fallbackContentPath = "";
         §§push("forceReload");
         §§push(false);
         if(!getTimer())
         {
            §§goto(addr11418);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   set("\x1a",false);
   set("e{invalid_utf8=198}","~");
   addr11418:
   §§pop()();
}
